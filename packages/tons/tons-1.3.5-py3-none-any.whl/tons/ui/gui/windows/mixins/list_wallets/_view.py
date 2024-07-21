import html
from functools import lru_cache
from typing import Sequence, Protocol, Optional, Dict, Callable, Iterator

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QListView, QComboBox
from tons.tonclient._client._base import AddressInfoResult
from tons.ui.gui.promoted_widgets import ContextSwitcherButton

from tons.ui.gui.utils import (theme_is_dark, slot_exc_handler, UpdateOnMouseMovementFilter, clean_html,
                               RichString, html_text_colored)
from tons.ui.gui.widgets import WalletListItemData, WalletListItemKind, WalletListModel, WalletListItem, \
    WalletListProxyModel, WalletListItemDelegate, WalletListItemDataRole, SortMode
from tons.ui.gui.windows.components.contact_kind_filter import ContactKindFilterSelectViewComponent, ContactKindFilter, \
    wallet_list_item_kinds


def _sort_by_mode_display_title(sort_mode: SortMode):
    matrix = {
        SortMode.name: "Name",
        SortMode.status: "Status",
        SortMode.comment: "Comment",
        SortMode.balance: "Balance",
        SortMode.last_activity: "Last activity"
    }
    return matrix[sort_mode]


class ListWalletsView:
    filter_changed = pyqtSignal()

    _list_view_wallets: QListView
    _combo_sort_by: QComboBox
    _line_edit_search: QLineEdit

    contact_kind_filter: Optional[ContactKindFilterSelectViewComponent]
    display_all_items_count: bool

    _button_subcontext_wallets: ContextSwitcherButton

    def init_list_wallets(self, display_transfer_arrow: bool = False, extra_hmargin: int = 0):
        self._list_model_wallets = WalletListModel()
        self._list_proxy_model_wallets = WalletListProxyModel(self._list_model_wallets)

        self._list_wallets_delegate = WalletListItemDelegate(display_transfer_arrow, extra_hmargin)
        if display_transfer_arrow:
            self._list_view_wallets.setMouseTracking(True)

        self._list_proxy_model_wallets.setDynamicSortFilter(False)  # very important

        self._list_view_wallets.setModel(self._list_proxy_model_wallets)
        self._list_view_wallets.setItemDelegate(self._list_wallets_delegate)

        self._improve_list_wallets_performance()
        self._init_sortby_combo()

        self._statistics: Dict[WalletListItemKind, int] = dict()
        self._clear_statistics()
        self._setup_list_wallets_signals()

    def _setup_list_wallets_signals(self):
        self._line_edit_search.textChanged.connect(self._on_search_prompt_changed)
        self._combo_sort_by.currentIndexChanged.connect(self._on_combo_sort_by_index_changed)
        try:
            setup_contact_kind_filter_signals = self.contact_kind_filter.setup_signals
        except AttributeError:
            pass
        else:
            setup_contact_kind_filter_signals(self)
        self.filter_changed.connect(self._display_filter)

    def _improve_list_wallets_performance(self):
        self._list_view_wallets.setUniformItemSizes(True)

    def _init_sortby_combo(self):
        for sort_mode in SortMode:
            self._combo_sort_by.addItem(_sort_by_mode_display_title(sort_mode), sort_mode)

    @property
    def search_prompt(self) -> str:
        return self._line_edit_search.text()

    @property
    def selected_wallet_model(self) -> Optional[WalletListItemData]:
        selected_indexes = self._list_view_wallets.selectedIndexes()
        if len(selected_indexes) == 1:
            selected_index = selected_indexes[0]
            if not selected_index.data(WalletListItemDataRole.visible.value):
                return None
            return selected_index.data(WalletListItemDataRole.application_data.value)
        elif len(selected_indexes) == 0:
            return None
        else:
            raise NotImplementedError

    @property
    def selected_kinds(self) -> Sequence[WalletListItemKind]:
        try:
            return self.contact_kind_filter.selected_kinds
        except AttributeError:
            return [WalletListItemKind.record, WalletListItemKind.local_contact, WalletListItemKind.global_contact]

    @pyqtSlot()
    @slot_exc_handler()
    def _on_search_prompt_changed(self):
        self._update_statistics()
        self.display_wallet_kind_count()
        self.filter_changed.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def on_kind_selected(self):
        self.filter_changed.emit()

    @pyqtSlot(int)
    @slot_exc_handler()
    def _on_combo_sort_by_index_changed(self, current_index: int):
        sort_mode: SortMode = self._combo_sort_by.itemData(current_index)
        self._set_wallets_sort_mode(sort_mode)
        self._sort_wallets()

    @property
    def _selected_sort_mode(self) -> SortMode:
        return self._combo_sort_by.currentData()

    def _wallet_list_items(self) -> Iterator[WalletListItem]:
        for row in range(self._list_model_wallets.rowCount()):
            yield self._list_model_wallets.item(row)

    def _set_wallets_sort_mode(self, sort_mode: SortMode):
        self._list_proxy_model_wallets.sort_mode = sort_mode

    def _sort_wallets(self):
        self._list_proxy_model_wallets.sort(0)

    def _invalidate_wallets_filter(self):
        self._list_proxy_model_wallets.invalidateFilter()

    def set_wallet_items(self, wallets: Sequence[WalletListItemData]):
        self.clear_wallets()

        for wallet_data in wallets:
            list_item = WalletListItem(wallet_data)
            self._list_model_wallets.appendRow(list_item)

        self._display_filter()
        self._update_statistics()
        self.display_wallet_kind_count()

        self._set_wallets_sort_mode(self._selected_sort_mode)
        self._sort_wallets()

    def clear_wallets(self):
        self._list_model_wallets.clear()

    @pyqtSlot()
    @slot_exc_handler()
    def _display_filter(self):
        for item in self._wallet_list_items():
            self._display_item_filter(item)
        self._invalidate_wallets_filter()

    def _display_item_filter(self, item: WalletListItem):
        wallet_data = item.wallet_data

        matches = bool(wallet_data.find(self.search_prompt))
        matches &= wallet_data.kind in self.selected_kinds

        item.visible = matches
        item.wallet_display_data = _wallet_data_with_highlighted_match(wallet_data, self.search_prompt)

    def _update_statistics(self):
        self._clear_statistics()
        for item in self._wallet_list_items():
            matches = self.search_prompt == '' or bool(item.wallet_data.find(self.search_prompt))
            self._statistics[item.wallet_data.kind] += int(matches)

    def _clear_statistics(self):
        for kind in WalletListItemKind:
            self._statistics[kind] = 0

    def get_displayed_item_count_by_kind(self, kind: WalletListItemKind) -> int:
        return self._statistics[kind]

    def display_wallet_kind_count(self):
        if self.contact_kind_filter is None:
            return

        for contact_kind in ContactKindFilter:
            if contact_kind == ContactKindFilter.all_items and not self.display_all_items_count:
                self.contact_kind_filter.set_wallet_kind_count(contact_kind, None)
                continue
            count = 0
            for kind in wallet_list_item_kinds(contact_kind):
                count += self.get_displayed_item_count_by_kind(kind)

            self.contact_kind_filter.set_wallet_kind_count(contact_kind, count)

    def hide_unnecessary_buttons(self, necessary_kind: ContactKindFilter):
        for kind in ContactKindFilter:
            button = self.contact_kind_filter.get_button(kind)
            if kind != necessary_kind:
                button.hide()
            else:
                button.clicked.emit()
                button.setDisabled(True)

    def show_all_buttons(self):
        for kind in ContactKindFilter:
            button = self.contact_kind_filter.get_button(kind)
            button.show()
            button.setDisabled(False)

        self.contact_kind_filter.click(ContactKindFilter.all_items)

    def set_address_info(self, get_address_info: Callable[[str], Optional[AddressInfoResult]]):
        at_least_one_changed = False

        for item in self._wallet_list_items():
            wallet_data = item.wallet_data
            address_info = get_address_info(wallet_data.address)
            if wallet_data.address_info == address_info:
                continue

            at_least_one_changed = True
            wallet_data.set_address_info(address_info)
            self._display_item_filter(item)

        if not at_least_one_changed:
            return

        self._invalidate_wallets_filter()
        self._sort_wallets()

    def _set_wallets_obscurity(self, obscure: bool):
        for item in self._wallet_list_items():
            item.obscure = obscure


def _wallet_data_with_highlighted_match(data: WalletListItemData, search_prompt: str):
    new_model_dict = data.dict()

    if search_prompt == '':
        return WalletListItemData(**new_model_dict)

    match = data.find(search_prompt)
    for var in vars(data):
        try:
            match_pos: int = match[var]
        except KeyError:
            continue

        prompt_len = len(search_prompt)

        val = getattr(data, var)

        if var in data.vars_with_user_text():
            val = html.escape(val)

        val = RichString(val)

        head = val[:match_pos]
        body = val[match_pos:match_pos + prompt_len]
        tail = val[match_pos + prompt_len:]

        body = _highlighted(clean_html(body))

        formatted_match = head + body + tail
        new_model_dict[var] = formatted_match

    return WalletListItemData(**new_model_dict)


@lru_cache
def _highlight_color() -> str:
    if theme_is_dark():
        return '#F5BF4F'
    # return '#0A40B0'
    return '#23a8ff'


def _highlighted(text: str) -> str:
    if len(text) == 0:
        return ''
    return html_text_colored(text, _highlight_color())


__all__ = ['ListWalletsView']
