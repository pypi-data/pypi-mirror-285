import contextlib
import copy
import json
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from typing import Sequence, Optional, Dict, Callable, Iterator, Tuple, Set

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QModelIndex, QItemSelectionModel, QItemSelection
from PyQt6.QtWidgets import QLineEdit, QListView, QComboBox

from tons.tonclient._client._base import NftItemInfoResult
from tons.ui.gui.promoted_widgets import ContextSwitcherButton

from tons.ui.gui.utils import theme_is_dark, slot_exc_handler, UpdateOnMouseMovementFilter, html_text_colored
from tons.ui.gui.widgets import DnsListItemData, DnsListItemKind, DnsListModel, DnsListItem, \
    DnsListProxyModel, DnsListItemDelegate, DnsListItemDataRole, DnsSortMode
from tons.ui.gui.windows.components.dns_kind_filter import DnsKindFilterSelectViewComponent, DnsKindFilter, \
    dns_list_item_kinds


def _sort_by_mode_display_title(sort_mode: DnsSortMode):
    matrix = {
        DnsSortMode.remaining: "Remaining",
        DnsSortMode.domain: "Domain",
        DnsSortMode.wallet: "Wallet",
    }
    return matrix[sort_mode]


class ListDnsView:
    dns_filter_changed = pyqtSignal()

    _list_view_dns: QListView
    _combo_dns_sort_by: QComboBox
    _line_edit_search: QLineEdit

    dns_kind_filter: Optional[DnsKindFilterSelectViewComponent]
    display_all_dns_items_count: bool

    _button_subcontext_dns: ContextSwitcherButton

    def init_list_dns(self):
        self._was_sorted = False
        self._prev_dns = {}

        self._list_model_dns = DnsListModel()
        self._list_proxy_model_dns = DnsListProxyModel(self._list_model_dns)
        self._list_dns_delegate = DnsListItemDelegate()
        self._list_view_dns.setMouseTracking(True)
        self._update_mouse_move_filter = UpdateOnMouseMovementFilter(self._list_view_dns.viewport())

        self._list_proxy_model_dns.setDynamicSortFilter(False)  # very important

        self._list_view_dns.setModel(self._list_proxy_model_dns)
        self._list_view_dns.setItemDelegate(self._list_dns_delegate)
        self._improve_list_dns_performance()
        self._init_dns_sortby_combo()

        self._dns_statistics: Dict[DnsListItemKind, int] = dict()
        self._clear_dns_statistics()
        self._setup_list_dns_signals()

    def _setup_list_dns_signals(self):
        self._line_edit_search.textChanged.connect(self._on_dns_search_prompt_changed)
        self._combo_dns_sort_by.currentIndexChanged.connect(self._on_combo_dns_sort_by_index_changed)
        try:
            setup_dns_kind_filter_signals = self.dns_kind_filter.setup_signals
        except AttributeError:
            pass
        else:
            setup_dns_kind_filter_signals(self)
        self.dns_filter_changed.connect(self._display_dns_filter)
        self.dns_filter_changed.connect(self._sort_dns)

    def _improve_list_dns_performance(self):
        self._list_view_dns.setUniformItemSizes(True)

    def _init_dns_sortby_combo(self):
        for sort_mode in DnsSortMode:
            self._combo_dns_sort_by.addItem(_sort_by_mode_display_title(sort_mode), sort_mode)

    @property
    def search_prompt(self) -> str:
        return self._line_edit_search.text()

    @property
    def selected_dns_model(self) -> Optional[DnsListItemData]:
        selected_indexes = self._list_view_dns.selectedIndexes()
        if len(selected_indexes) == 1:
            selected_index = selected_indexes[0]
            if not selected_index.data(DnsListItemDataRole.visible.value):
                return None
            return selected_index.data(DnsListItemDataRole.application_data.value)
        elif len(selected_indexes) == 0:
            return None
        else:
            raise NotImplementedError

    @property
    def visible_dns_items(self) -> Iterator[DnsListItemData]:
        for index in self._dns_list_sorted_indexes():
            yield self._list_proxy_model_dns.data(index, role=DnsListItemDataRole.application_data.value)

    @property
    def is_skeleton(self) -> bool:
        item = self._list_model_dns.item(0)
        if item is not None:
            return item.data(role=DnsListItemDataRole.skeleton.value)

        return False

    @pyqtSlot()
    @slot_exc_handler()
    def on_dns_kind_selected(self):
        self.dns_filter_changed.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_dns_search_prompt_changed(self):
        self._update_dns_statistics()
        self.display_dns_kind_count()
        self.dns_filter_changed.emit()

    @pyqtSlot(int)
    @slot_exc_handler()
    def _on_combo_dns_sort_by_index_changed(self, current_index: int):
        sort_mode: DnsSortMode = self._combo_dns_sort_by.itemData(current_index)
        self._set_dns_sort_mode(sort_mode)
        self._sort_dns()

    @property
    def _selected_dns_sort_mode(self) -> DnsSortMode:
        return self._combo_dns_sort_by.currentData()

    def _dns_list_items(self) -> Iterator[DnsListItem]:
        for row in range(self._list_model_dns.rowCount()):
            yield self._list_model_dns.item(row)

    def _dns_list_sorted_indexes(self) -> Iterator[QModelIndex]:
        for row in range(self._list_proxy_model_dns.rowCount()):
            yield self._list_proxy_model_dns.index(row, 0)

    def _set_dns_sort_mode(self, dns_sort_mode: DnsSortMode):
        self._list_proxy_model_dns.dns_sort_mode = dns_sort_mode

    def _sort_dns(self):
        self._list_proxy_model_dns.sort(0)

    def _invalidate_dns_filter(self):
        self._list_proxy_model_dns.invalidateFilter()

    def reset_dns_items(self):
        self._prev_dns = {}
        self._was_sorted = False
        self.clear_dns()
        self._update_dns_statistics()
        self.display_dns_kind_count()

    def set_dns_items(self, dns_dict: Dict[str, Dict[str, DnsListItemData]], all_loaded: bool, dns_num: int):
        if dns_num == 0 and not all_loaded:
            self._show_skeletons()
            return

        self._clear_skeletons()
        if dns_dict != self._prev_dns:
            self._was_sorted = False
            self._prev_dns = dns_dict
            already_shown = self._change_old_records(dns_dict)
            with self._preserve_selected_dns():
                self._append_new_records(dns_dict, already_shown)

            self._display_dns_filter()
            self._update_dns_statistics()
            self.display_dns_kind_count()

        if all_loaded and not self._was_sorted:
            self._was_sorted = True
            self._set_dns_sort_mode(self._selected_dns_sort_mode)
            self._sort_dns()

    def _clear_skeletons(self):
        row_count = self._list_model_dns.rowCount()
        row_idx = 0
        while row_idx < row_count:
            item_data: Optional[DnsListItem] = self._list_model_dns.item(row_idx)
            if item_data is None or item_data.skeleton or item_data.dns_data is None:
                self._list_model_dns.removeRow(row_idx)
                row_idx -= 1
                row_count -= 1
            row_idx += 1

    def _change_old_records(self, dns_dict) -> Set:
        already_shown = set()
        row_count = self._list_model_dns.rowCount()
        row_idx = 0

        while row_idx < row_count:
            item_data: Optional[DnsListItem] = self._list_model_dns.item(row_idx)
            if item_data is not None:
                item_dns_data = item_data.dns_data
                if item_dns_data.wallet_address not in dns_dict:
                    self._list_model_dns.removeRow(row_idx)
                    row_idx -= 1
                    row_count -= 1
                elif item_dns_data.domain in dns_dict[item_dns_data.wallet_address]:
                    already_shown.add(item_dns_data.domain)
                    if item_dns_data != dns_dict[item_dns_data.wallet_address][item_dns_data.domain]:
                        item_dns_data.set_dns_info(dns_dict[item_dns_data.wallet_address][item_dns_data.domain])
                        self._display_dns_item_filter(item_data)

                row_idx += 1

        return already_shown

    def _append_new_records(self, dns_dict, already_shown):
        for wallet_addr in dns_dict:
            for dns_domain in dns_dict[wallet_addr]:
                if dns_domain not in already_shown:
                    list_item = DnsListItem(dns_dict[wallet_addr][dns_domain],
                                            filtered_by_wallet=self.dns_kind_filter.filtered_by_wallet,
                                            skeleton=False)
                    self._list_model_dns.appendRow(list_item)

    def _show_skeletons(self):
        self.clear_dns()
        self._update_dns_statistics()
        self.display_dns_kind_count()
        for dns_data in self._dns_skeleton_list:
            list_item = DnsListItem(dns_data, filtered_by_wallet=False, skeleton=True)
            self._list_model_dns.appendRow(list_item)

    def clear_dns(self):
        self._list_model_dns.clear()

    @property
    def _dns_skeleton_list(self) -> Sequence[DnsListItemData]:
        return [DnsListItemData.skeleton() for _ in range(10)]

    @contextlib.contextmanager
    def _preserve_selected_dns(self):
        current_item: Optional[DnsListItemData] = self.selected_dns_model
        if current_item is not None:
            domain = current_item.domain
            yield

            for index in self._dns_list_sorted_indexes():
                data = self._list_proxy_model_dns.data(index, role=DnsListItemDataRole.application_data.value)
                if data.domain == domain:
                    self._list_view_dns.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)

                    break
        else:
            yield

    @pyqtSlot()
    @slot_exc_handler()
    def _display_dns_filter(self):
        for item in self._dns_list_items():
            self._display_dns_item_filter(item)
        self._invalidate_dns_filter()

    def _display_dns_item_filter(self, item: DnsListItem):
        dns_data = item.dns_data

        matches = bool(dns_data.find(self.search_prompt))
        matches &= self.dns_kind_filter.match(dns_data)

        item.visible = matches
        item.dns_display_data = _dns_data_with_highlighted_match(dns_data, self.search_prompt)

    def _update_dns_statistics(self):
        self._clear_dns_statistics()
        for item in self._dns_list_items():
            matches = self.search_prompt == '' or bool(item.dns_data.find(self.search_prompt))
            self._dns_statistics[item.dns_data.kind] += int(matches)

    def _clear_dns_statistics(self):
        for kind in DnsListItemKind:
            self._dns_statistics[kind] = 0

    def get_dns_displayed_item_count_by_kind(self, kind: DnsListItemKind) -> int:
        return self._dns_statistics[kind]

    def display_dns_kind_count(self):
        if self.dns_kind_filter is None:
            return

        for dns_kind in DnsKindFilter:
            if dns_kind == DnsKindFilter.all_items and not self.display_all_dns_items_count:
                self.dns_kind_filter.set_dns_kind_count(dns_kind, None)
                continue

            count = 0
            for kind in dns_list_item_kinds(dns_kind):
                count += self.get_dns_displayed_item_count_by_kind(kind)

            self.dns_kind_filter.set_dns_kind_count(dns_kind, count)

    def show_all_buttons(self):
        for kind in DnsKindFilter:
            button = self.dns_kind_filter.get_button(kind)
            button.show()
            button.setDisabled(False)

        self.dns_kind_filter.click(DnsKindFilter.all_items)

    def set_dns_info(self, get_dns_info: Callable[[str, str], Optional[NftItemInfoResult]]):
        raise NotImplementedError
        at_least_one_changed = False
        for item in self._dns_list_items():
            dns_data = item.dns_data
            nft_info = get_dns_info(dns_data.wallet_address, dns_data.domain)
            if dns_data.nft_info == nft_info:
                continue

            at_least_one_changed = True
            dns_data.set_dns_info(nft_info)
            self._display_item_filter(item)

        if not at_least_one_changed:
            return

        self._invalidate_dns_filter()
        self._sort_dns()

    def _set_dns_obscurity(self, obscure: bool):
        for item in self._dns_list_items():
            item.obscure = obscure


def _dns_data_with_highlighted_match(data: DnsListItemData, search_prompt: str):
    new_model_dict = data.dict()

    if search_prompt == '':
        return DnsListItemData(**new_model_dict)

    match = data.find(search_prompt)
    for var in vars(data):
        try:
            match_pos: int = match[var]
        except KeyError:
            continue

        prompt_len = len(search_prompt)
        val = getattr(data, var)

        head = val[:match_pos]
        body = _highlighted(val[match_pos:match_pos + prompt_len])
        tail = val[match_pos + prompt_len:]

        formatted_match = head + body + tail
        new_model_dict[var] = formatted_match

    return DnsListItemData(**new_model_dict)


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


__all__ = ['ListDnsView']
