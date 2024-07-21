import contextlib
import typing
from decimal import Decimal
from enum import Enum, auto
from typing import Sequence, Protocol

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSlot, QObject, QEvent, pyqtSignal, QModelIndex, QPoint, QRect
from PyQt6.QtGui import QAction, QGuiApplication, QCursor
from PyQt6.QtWidgets import QPushButton, QAbstractButton, QWidget, QLineEdit, QMenu, \
    QLabel, QStatusBar, QComboBox, QMessageBox, QListView

from tons import settings, version
from tons.ui.gui.promoted_widgets import ContextSwitcherButton
from tons.ui.gui.services import ton_usd_price
from tons.ui.gui.uis import MainWindowUI
from tons.ui.gui.utils import ObscurableTextDisplay, windows, set_icon, open_browser, ForbidKeyMovementEventFilter
from tons.ui.gui.utils import slot_exc_handler, TextDisplayProperty, \
    pretty_balance, ContactLocation, \
    LocalWhitelistLocation, show_message_box_warning, pretty_fiat_balance, \
    qt_exc_handler
from tons.ui.gui.widgets import SideBarListItemModel, WalletListItemKind, WalletListItemData, SideBarListItemKind, \
    WalletListItemDataRole, RefreshDnsMenuModel, RefreshDnsMenuView, DnsItemRectangles, DnsListItemDataRole, \
    DnsListItemData, SideBarListItemDelegate, SideBarListItem
from tons.ui.gui.widgets._side_bar_list_item._list_model import SideBarListModel
from tons.ui.gui.widgets.notification_bar import NotificationBar
from tons.ui.gui.widgets._wallet_list_item._delegate import _get_if_mouse_hovers_over_arrow
from tons.ui.gui.windows.components.contact_kind_filter import ContactKindFilterSelectViewComponent
from tons.ui.gui.windows.components.dns_kind_filter import DnsKindFilterSelectViewComponent
from tons.ui.gui.windows.components.keystore_window_subcontext import KeystoreWindowSubcontextViewComponent, \
    KeystoreWindowSubcontext
from tons.ui.gui.windows.components.status_bar import StatusBarViewComponent
from tons.ui.gui.windows.mixins.list_dns import ListDnsView
from tons.ui.gui.windows.mixins.list_wallets import ListWalletsView
from tons.ui.gui.windows.mixins.shortcuts.main_window_shortcuts import MainWindowViewShortcutsMixin


class Presenter(Protocol):
    def on_wallet_selected(self): ...
    def on_dns_selected(self): ...
    def on_new_wallet(self): ...
    def on_import_from_mnemonics(self): ...
    def on_import_from_private_key(self): ...
    def on_create_batch(self): ...
    def on_create_keystore(self): ...
    def on_create_contact(self): ...
    def on_obscurity_changed(self): ...
    def on_create_local_contact(self): ...
    def on_preferences(self): ...
    def on_transfer(self): ...
    def on_transfer_from(self): ...
    def on_transfer_to(self): ...
    def on_open_transactions_history(self): ...
    def on_closed(self): ...
    def on_sidebar_item_selected(self, sidebar_item: SideBarListItemModel): ...
    def on_show_wallet_context_menu(self, wallet: WalletListItemData): ...
    def on_show_dns_context_menu(self, dns: DnsListItemData): ...
    def on_fetch_keystores_balance(self): ...

    def on_dns_refresh_selected_list_item(self): ...
    def on_backup_keystore(self, keystore_name: str): ...
    def on_export_keystore(self, keystore_name: str): ...
    def on_import_keystore(self): ...


class NewWalletKeystoreMenu(QMenu):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)
        self.action_new = QAction('New wallet...', self)
        self.action_import_mnemonics = QAction('Import wallet from mnemonics...', self)
        self.action_import_pk = QAction('Import wallet from private key...', self)
        self.action_batch = QAction('New multiple wallets...', self)
        self.action_new_local_contact = QAction('New local contact...', self)

        for action in [self.action_new, self.action_import_mnemonics, self.action_import_pk, self.action_batch]:
            self.addAction(action)

        self.addSeparator()
        self.addAction(self.action_new_local_contact)


class TransferMenu(QMenu):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)
        # icon_from = get_icon("arrow-transfer-from.svg")
        self.action_transfer_from = QAction('Transfer from...', self)
        # icon_to = get_icon("arrow-transfer-to.svg")
        self.action_transfer_to = QAction('Transfer to...', self)
        for action in [self.action_transfer_from, self.action_transfer_to]:
            self.addAction(action)


class NewWalletButtonState(Enum):
    keystore = auto()
    global_whitelist = auto()


class EyeButtonState(Enum):
    show = auto()
    hide = auto()


class MainWindowView(QtWidgets.QMainWindow, MainWindowViewShortcutsMixin, ListWalletsView, ListDnsView):
    # TODO separate sidebar into a separate mixin
    _closed = pyqtSignal()

    _sidebar_item_selected = pyqtSignal(SideBarListItemModel)

    _transfer = pyqtSignal()
    _transfer_from = pyqtSignal([], [WalletListItemData])
    _transfer_to = pyqtSignal([], [WalletListItemData])

    _refresh_dns_item = pyqtSignal()

    _create_global_contact = pyqtSignal()
    _open_transactions_history = pyqtSignal()
    _create_local_contact = pyqtSignal()

    _backup_keystore = pyqtSignal(str)
    _export_keystore = pyqtSignal(str)
    _import_keystore = pyqtSignal()

    _show_in_scanner = pyqtSignal(str)

    _obscurity_changed = pyqtSignal()

    _show_wallet_context_menu = pyqtSignal(WalletListItemData)
    _show_dns_context_menu = pyqtSignal(DnsListItemData)

    search_prompt = TextDisplayProperty("lineEditSearch")

    _list_model_keystores: SideBarListModel
    _list_model_whitelists: SideBarListModel
    _sidebar_delegate: SideBarListItemDelegate

    def __init__(self):
        super().__init__()
        self._ui = MainWindowUI()
        self._ui.setupUi(self)
        # self._status_bar.hide()
        self._cur_subcontext = KeystoreWindowSubcontext.wallets
        self._change_to_wallets_subcontext()
        self._exit_search_mode()

        self._total_balance = ObscurableTextDisplay(self._label_balance_ton, True)
        self._total_balance_fiat = ObscurableTextDisplay(self._label_balance_fiat, True)

        self._forbid_key_movement_event_filter = ForbidKeyMovementEventFilter(self._list_view_keystores)
        self._install_event_filters()

        self._menu_new_wallet = NewWalletKeystoreMenu(parent=self)
        self._menu_transfer = TransferMenu(parent=self)
        self._refresh_dns_menu = RefreshDnsMenuView(parent=self)

        self._button_refresh_dns.setMenu(self._refresh_dns_menu)

        self.contact_kind_filter = ContactKindFilterSelectViewComponent(self._button_all_items,
                                                                        self._button_keystore_wallets,
                                                                        self._button_local_whitelist,
                                                                        self._button_global_whitelist)
        self.dns_kind_filter = DnsKindFilterSelectViewComponent(self._button_dns_all_items,
                                                                self._button_dns_owned,
                                                                self._button_dns_taken,
                                                                self._button_dns_by_wallet)
        self._subcontext_component = KeystoreWindowSubcontextViewComponent(self._button_subcontext_wallets,
                                                                           self._button_subcontext_dns)

        self._notification_bar = NotificationBar(self._ui.listViewContainer, parent=self)
        self.status_bar = StatusBarViewComponent(self._notification_bar)

        self.display_all_items_count = False
        self.display_all_dns_items_count = True
        self.init_sidebar()
        self.init_list_wallets(display_transfer_arrow=True)
        self.init_list_dns()

        self._new_wallet_button_state: NewWalletButtonState = ...
        self._selected_sidebar_item_model: SideBarListItemModel = ...
        self._eye_button_state: EyeButtonState = ...

        self._sensitive_data_obscure: bool = ...

        self.set_zero_values()
        self._set_tons_version()
        self._setup_signals()
        self._setup_shortcuts()

        self._hide_unnecessary_elements()

    def _hide_unnecessary_elements(self):
        self._label_wallet_count.setText('')
        self._status_bar.hide()

    def _set_tons_version(self):
        self._label_tons_version.setText(f'Tons v{version.__version__}')

    def set_zero_values(self):
        self._label_keystore_name.setText('Please select keystore')
        self._sensitive_data_obscure = False
        self._eye_button_state = EyeButtonState.show
        self._selected_sidebar_item_model = None
        self.set_total_balance(None)
        self._update_context_menu_buttons_ability()
        self._update_new_wallet_button_state()
        self._disable_keystore_actions()
        self.change_to_empty_subcontext()

    def init_update_keystores_button(self):
        self._button_fetch_keystores_balance.setEnabled(True)

    @property
    def sensitive_data_obscure(self) -> bool:
        return self._sensitive_data_obscure

    def _set_uniform_sizes(self):
        """ Reduces overhead """
        # TODO refactor (rename to _improve_sidebar_performance)
        self._list_view_whitelists.setUniformItemSizes(True)
        # self._list_view_keystores.setUniformItemSizes(True)

    @qt_exc_handler
    def eventFilter(self, object_: typing.Optional['QObject'], event: typing.Optional['QEvent']) -> bool:
        if object_ == self._line_edit_search:
            if event.type() == QEvent.Type.FocusOut:
                if self._line_edit_search.text() == '':
                    self._exit_search_mode()
            elif event.type() == QEvent.Type.KeyPress:
                assert isinstance(event, QtGui.QKeyEvent)
                if event.key() == Qt.Key.Key_Escape:
                    self._line_edit_search.setText('')
                    self._exit_search_mode()

        return False

    def closeEvent(self, a0: typing.Optional[QtGui.QCloseEvent]) -> None:
        self._closed.emit()

    def _get_transfer_menu(self) -> QMenu:
        menu = QMenu()
        action_from = QAction('Transfer from selected wallet', self)
        action_to = QAction('Transfer to selected wallet', self)
        for action in [action_from, action_to]:
            menu.addAction(action)
        return menu

    def _setup_signals(self):
        self._button_search.clicked.connect(self._on_search_clicked)
        self._button_exit_search.clicked.connect(self._on_search_exit_clicked)
        self._button_eye.clicked.connect(self._on_button_eye_clicked)
        self._line_edit_search.textEdited.connect(self._on_search_text_edited)

        self._action_quit.triggered.connect(self._on_quit)
        self._action_new_global_contact.triggered.connect(self._on_create_global_contact)
        self._action_transactions_history.triggered.connect(self._on_open_transactions_history)

        self._action_documentation.triggered.connect(self._on_menu_documentation)
        self._action_support.triggered.connect(self._on_menu_support)
        self._action_shortcuts.triggered.connect(self._on_menu_shortcuts)

        self._menu_new_wallet.action_new_local_contact.triggered.connect(self._on_create_local_contact)

        for menu in [self._menu_transfer, ]:
            menu.action_transfer_from.triggered.connect(self._on_action_transfer_from_triggered)
            menu.action_transfer_to.triggered.connect(self._on_action_transfer_to_triggered)

        self._list_view_keystores.clicked.connect(self._on_keystore_selected)
        self._list_view_whitelists.clicked.connect(self._on_whitelist_selected)

        self._list_view_wallets.clicked.connect(self._on_wallet_clicked)
        self._list_view_wallets.pressed.connect(self._on_wallet_pressed)
        self._list_view_dns.clicked.connect(self._on_dns_table_clicked)
        self._list_view_dns.pressed.connect(self._on_dns_pressed)

        self._button_new_wallet.clicked.connect(self._on_button_new_wallet_clicked)

        self.filter_changed.connect(self._on_filter_changed)  # TODO move to _setup_list_dns_signals()
        self.dns_filter_changed.connect(self._on_filter_changed)  # TODO move to _setup_list_dns_signals()
        self._button_dns_all_items.clicked.connect(self._on_dns_all_items_filter_clicked)

        self._action_backup_keystore.triggered.connect(self._on_backup_keystore)
        self._action_export_keystore.triggered.connect(self._on_export_keystore)
        self._action_import_keystore.triggered.connect(self._on_import_keystore)

        self._button_show_transaction_history.clicked.connect(self._on_open_transactions_history)

        self._subcontext_component.setup_signals(self)

    def setup_signals(self, presenter: Presenter):
        self._action_new_keystore.triggered.connect(presenter.on_create_keystore)
        self._action_new_wallet.triggered.connect(presenter.on_new_wallet)
        self._action_import_wallet_from_mnemonics.triggered.connect(presenter.on_import_from_mnemonics)
        self._action_import_wallet_from_private_key.triggered.connect(presenter.on_import_from_private_key)
        self._action_preferences.triggered.connect(presenter.on_preferences)
        self._obscurity_changed.connect(presenter.on_obscurity_changed)
        self._action_new_multiple_wallets.triggered.connect(presenter.on_create_batch)

        self._menu_new_wallet.action_batch.triggered.connect(presenter.on_create_batch)
        self._menu_new_wallet.action_import_mnemonics.triggered.connect(presenter.on_import_from_mnemonics)
        self._menu_new_wallet.action_import_pk.triggered.connect(presenter.on_import_from_private_key)
        self._menu_new_wallet.action_new.triggered.connect(presenter.on_new_wallet)

        self._transfer.connect(presenter.on_transfer)
        self._transfer_from.connect(presenter.on_transfer_from)
        self._transfer_from[WalletListItemData].connect(presenter.on_transfer_from)
        self._transfer_to.connect(presenter.on_transfer_to)
        self._transfer_to[WalletListItemData].connect(presenter.on_transfer_to)

        self._refresh_dns_item.connect(presenter.on_dns_refresh_selected_list_item)

        self._open_transactions_history.connect(presenter.on_open_transactions_history)

        self._create_global_contact.connect(presenter.on_create_contact)
        self._create_local_contact.connect(presenter.on_create_local_contact)

        self._sidebar_item_selected.connect(presenter.on_sidebar_item_selected)
        self._show_in_scanner.connect(presenter.on_show_in_scanner)

        self._list_view_wallets.doubleClicked.connect(presenter.on_wallet_selected)
        self._list_view_dns.doubleClicked.connect(presenter.on_dns_selected)

        self._closed.connect(presenter.on_closed)
        self._show_wallet_context_menu.connect(presenter.on_show_wallet_context_menu)
        self._show_dns_context_menu.connect(presenter.on_show_dns_context_menu)

        self._button_fetch_keystores_balance.clicked.connect(presenter.on_fetch_keystores_balance)

        self._export_keystore.connect(presenter.on_export_keystore)
        self._backup_keystore.connect(presenter.on_backup_keystore)
        self._import_keystore.connect(presenter.on_import_keystore)

        self._refresh_dns_menu.setup_signals(presenter)

    def _sidebar_view_model_pairs(self) -> Sequence[typing.Tuple[QListView, SideBarListModel]]:
        return [
            (self._list_view_keystores, self._list_model_keystores),
            (self._list_view_whitelists, self._list_model_whitelists)
        ]

    @pyqtSlot()
    @slot_exc_handler()
    def _on_filter_changed(self):
        self._update_context_menu_buttons_ability()

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_wallet_clicked(self, index: QModelIndex):
        visual_rect: QRect = self._list_view_wallets.visualRect(index)

        mouse_position_global = QCursor().pos()
        mouse_position = self._list_view_wallets.viewport().mapFromGlobal(mouse_position_global)

        mouse_position -= visual_rect.topLeft()
        visual_rect.translate(-visual_rect.topLeft())

        hovers_transfer_button = _get_if_mouse_hovers_over_arrow(mouse_position, visual_rect)

        if hovers_transfer_button:
            data: WalletListItemData = index.data(WalletListItemDataRole.application_data.value)
            if data.kind == WalletListItemKind.record:
                self._transfer_from[WalletListItemData].emit(data)
            elif data.kind in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:
                self._transfer_to[WalletListItemData].emit(data)
            else:
                raise NotImplementedError

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_dns_table_clicked(self, index: QModelIndex):
        visual_rect: QRect = self._list_view_dns.visualRect(index)
        mouse_position_global = QCursor().pos()
        mouse_position = self._list_view_dns.viewport().mapFromGlobal(mouse_position_global)
        mouse_position -= visual_rect.topLeft()
        visual_rect.translate(-visual_rect.topLeft())
        dns_data: DnsListItemData = self._list_proxy_model_dns.data(index, role=DnsListItemDataRole.application_data.value)
        rectangles = DnsItemRectangles(dns_data, visual_rect)
        if rectangles.filter_by_this_wallet.contains(mouse_position):
            self.dns_kind_filter.set_selected_wallet(dns_data.wallet_name)
            self._button_dns_taken.hide()
            self._button_dns_owned.hide()
            self._button_dns_by_wallet.show()
            self._set_dns_filtered_by_wallet(True)

        elif rectangles.button_hover.contains(mouse_position):
            self._refresh_dns_item.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_dns_all_items_filter_clicked(self):
        self.dns_kind_filter.set_selected_wallet(None)
        self._button_dns_taken.show()
        self._button_dns_owned.show()
        self._button_dns_by_wallet.hide()
        self._set_dns_filtered_by_wallet(False)

    def _set_dns_filtered_by_wallet(self, filtered_by_wallet: bool):
        for item in self._dns_list_items():
            item.filtered_by_wallet = filtered_by_wallet

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_wallet_pressed(self, index: QModelIndex):
        if QGuiApplication.mouseButtons() == Qt.MouseButton.RightButton:
            data = index.data(WalletListItemDataRole.application_data.value)
            self._show_wallet_context_menu.emit(data)

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_dns_pressed(self, index: QModelIndex):
        if QGuiApplication.mouseButtons() == Qt.MouseButton.RightButton:
            data = index.data(DnsListItemDataRole.application_data.value)
            self._show_dns_context_menu.emit(data)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_action_transfer_from_triggered(self):
        assert self.selected_wallet_model.kind == WalletListItemKind.record
        self._transfer_from.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_action_transfer_to_triggered(self):
        self._transfer_to.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_create_global_contact(self):
        self._create_global_contact.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_menu_documentation(self):
        open_browser(settings.DOCUMENTATION_LINK)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_menu_support(self):
        open_browser(settings.SUPPORT_LINK)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_menu_shortcuts(self):
        open_browser(settings.DOCUMENTATION_SHORTCUTS_LINK)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_open_transactions_history(self):
        self._open_transactions_history.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_create_local_contact(self):
        self._create_local_contact.emit()

    @classmethod
    def _get_sidebar_item_data_from_index(cls, list_model: SideBarListModel, index: QModelIndex) -> \
            SideBarListItemModel:
        list_item = list_model.itemFromIndex(index)
        assert isinstance(list_item, SideBarListItem)
        return list_item.item_model

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_keystore_selected(self, index: QModelIndex):
        self._list_view_whitelists.setCurrentIndex(QModelIndex())
        list_item_model = self._get_sidebar_item_data_from_index(self._list_model_keystores, index)
        self._selected_sidebar_item_model = list_item_model
        self._update_context_menu_buttons_ability()
        self._update_new_wallet_button_state()

        self._sidebar_item_selected.emit(list_item_model)
        self._enable_keystore_actions()

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_whitelist_selected(self, index: QModelIndex):
        self._list_view_keystores.setCurrentIndex(QModelIndex())
        list_item_model = self._get_sidebar_item_data_from_index(self._list_model_whitelists, index)
        self._selected_sidebar_item_model = list_item_model

        self._update_context_menu_buttons_ability()
        self._update_new_wallet_button_state()
        self._sidebar_item_selected.emit(list_item_model)
        self._disable_keystore_actions()

    @property
    def _keystore_actions(self) -> Sequence[QAction]:
        return [self._action_export_keystore, self._action_backup_keystore, self._action_new_wallet,
                self._action_import_wallet_from_mnemonics, self._action_new_multiple_wallets,
                self._action_import_wallet_from_private_key]

    def _disable_keystore_actions(self):
        for action in self._keystore_actions:
            action.setEnabled(False)

    def _enable_keystore_actions(self):
        for action in self._keystore_actions:
            action.setEnabled(True)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_quit(self):
        self.close()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_search_clicked(self):
        self._enter_search_mode()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_search_exit_clicked(self):
        self._line_edit_search.setText('')
        self._exit_search_mode()

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_search_text_edited(self, txt: str):
        pass

    @pyqtSlot()
    @slot_exc_handler()
    def _on_button_new_wallet_clicked(self):
        assert self._new_wallet_button_state == NewWalletButtonState.global_whitelist
        self._create_global_contact.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_show_in_scanner(self):
        selected_wallet = self.selected_wallet_model
        self._show_in_scanner.emit(selected_wallet.address)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_button_eye_clicked(self):
        if self._eye_button_state == EyeButtonState.show:
            self._sensitive_data_obscure = True
            self._eye_button_state = EyeButtonState.hide
            set_icon(self._button_eye, 'eye-slash-solid.svg')
        else:
            self._sensitive_data_obscure = False
            self._eye_button_state = EyeButtonState.show
            set_icon(self._button_eye, 'eye-solid.svg')

        self._update_balance_obscurity()
        self._update_sidebar_obscurity()
        self.update_wallets_obscurity()
        self.update_dns_obscurity()
        self._update_transaction_history_ability()

        self._obscurity_changed.emit()

        # self.status_bar.display(
        #     StatusBarMessageModel(
        #         message='Eye :)'
        #     )
        # )

    @pyqtSlot()
    @slot_exc_handler()
    def on_subcontext_switched(self):
        if self._subcontext_component.selected_subcontext != self._cur_subcontext:
            self._cur_subcontext = self._subcontext_component.selected_subcontext
            self.setUpdatesEnabled(False)
            try:
                self.change_to_correct_subcontext()
            finally:
                self.setUpdatesEnabled(True)
        self._exit_search_mode()

    def change_to_empty_subcontext(self):
        self._list_view_dns.hide()
        self._button_refresh_dns.hide()
        self._button_new_wallet.show()
        self._button_search.setEnabled(False)
        self._dns_filter_buttons_block.hide()
        self._combo_dns_sort_by.hide()
        self._list_view_wallets.hide()
        self._wallets_filter_buttons_block.hide()
        self._widget_sort_by.hide()

    def change_to_correct_subcontext(self):
        self._button_search.setEnabled(True)
        self._widget_sort_by.show()
        if self._subcontext_component.selected_subcontext == KeystoreWindowSubcontext.wallets:
            self._change_to_wallets_subcontext()
        elif self._subcontext_component.selected_subcontext == KeystoreWindowSubcontext.dns:
            self._change_to_dns_subcontext()

    def set_global_whitelist_subcontext(self):
        self._subcontext_component.click(KeystoreWindowSubcontext.wallets)
        self.change_to_correct_subcontext()

    def _change_to_wallets_subcontext(self):
        self._list_view_dns.hide()
        self._dns_filter_buttons_block.hide()
        self._button_refresh_dns.hide()
        self._combo_dns_sort_by.hide()

        self._list_view_wallets.show()
        self._button_new_wallet.show()
        self._wallets_filter_buttons_block.show()
        self._combo_sort_by.show()

    def _change_to_dns_subcontext(self):
        self._list_view_wallets.hide()
        self._combo_sort_by.hide()
        self._button_new_wallet.hide()
        self._wallets_filter_buttons_block.hide()

        self._list_view_dns.show()
        self._button_refresh_dns.show()
        self._combo_dns_sort_by.show()
        self._dns_filter_buttons_block.show()

    def _update_transaction_history_ability(self):
        self._button_show_transaction_history.setDisabled(self._sensitive_data_obscure)
        self._action_transactions_history.setDisabled(self._sensitive_data_obscure)

    def _update_sidebar_obscurity(self):
        for list_view, list_model in self._sidebar_view_model_pairs():
            for row_idx in range(list_model.rowCount()):
                list_item = list_model.item(row_idx)
                assert isinstance(list_item, SideBarListItem)
                list_item.obscure = self._sensitive_data_obscure

    def update_wallets_obscurity(self):
        self._set_wallets_obscurity(self._sensitive_data_obscure)

    def update_dns_obscurity(self):
        self._set_dns_obscurity(self._sensitive_data_obscure)

    @property
    def _widget_sort_by(self) -> QWidget:
        return self._ui.widgetSortBy

    def _enter_search_mode(self):
        self._button_search.hide()
        self._button_new_wallet.hide()
        # self._button_refresh_dns.hide()
        if self._cur_subcontext == KeystoreWindowSubcontext.wallets:
            self._vertical_line.hide()
        self._widget_search.show()
        self._line_edit_search.setFocus()

    def _exit_search_mode(self):
        self._button_search.show()
        if self._cur_subcontext == KeystoreWindowSubcontext.wallets:
            self._button_new_wallet.show()
        elif self._cur_subcontext == KeystoreWindowSubcontext.dns:
            self._button_refresh_dns.show()
        self._vertical_line.show()
        self._line_edit_search.setText('')
        self._widget_search.hide()

    def set_outdated(self):
        self._label_tons_version_update.setVisible(True)

    def warn_outdated(self):
        link = 'https://tonfactory.github.io/tons-docs/installation#update'
        if windows():
            link = f'<a href="{link}">{link}</a>'
        show_message_box_warning("Warning", 'Tons is outdated!\n\n'
                                            'Please, see the update instructions: '
                                            f'{link}')

    def warn_workdir_error(self, workdir: str):
        show_message_box_warning("Error", f'Tons setup error!'
                                          f'\n\nDirectory "{workdir}" inaccessible or unmounted. '
                                          f'\nPlease change the working directory in the preferences.')

    @property
    def _label_tons_version_update(self):
        return self._ui.tonsVersionUpdateLabel

    @property
    def list_name(self) -> str:
        return self._label_keystore_name.text()

    @list_name.setter
    def list_name(self, value: str):
        label = self._label_keystore_name
        label.setText(value)

    @property
    def _button_all_items(self) -> QPushButton:
        return self._ui.pushButtonAllItems

    @property
    def _button_keystore_wallets(self) -> QPushButton:
        return self._ui.pushButtonKeystoreWallets

    @property
    def _button_local_whitelist(self) -> QPushButton:
        return self._ui.pushButtonLocalWhitelist

    @property
    def _button_global_whitelist(self) -> QPushButton:
        return self._ui.pushButtonGlobalWhitelist

    @property
    def _button_dns_all_items(self) -> QPushButton:
        return self._ui.pushButtonDnsAllItems

    @property
    def _button_dns_owned(self) -> QPushButton:
        return self._ui.pushButtonDnsOwned

    @property
    def _button_dns_taken(self) -> QPushButton:
        return self._ui.pushButtonDnsTaken

    @property
    def _button_dns_by_wallet(self) -> QPushButton:
        return self._ui.pushButtonDnsByWallet

    @property
    def _button_show_transaction_history(self) -> QPushButton:
        return self._ui.pushButtonTransactionHistory

    @property
    def _wallets_filter_buttons_block(self) -> QWidget:
        return self._ui.widgetFilterButtons

    @property
    def _dns_filter_buttons_block(self) -> QWidget:
        return self._ui.widgetFilterDnsButtons

    @property
    def _button_subcontext_wallets(self) -> ContextSwitcherButton:
        return self._ui.pushButtonSubcontextWallets

    @property
    def _button_subcontext_dns(self) -> ContextSwitcherButton:
        return self._ui.pushButtonSubcontextDns

    @property
    def _button_fetch_keystores_balance(self) -> QPushButton:
        return self._ui.pushButtonFetchKeystoresBalance

    @property
    def _widget_search(self) -> QWidget:
        return self._ui.widgetSearch

    @property
    def _widget_upper_header_center(self) -> QWidget:
        return self._ui.widgetUpperHeaderCenter

    @property
    def _list_view_wallets(self) -> QListView:
        return self._ui.listViewWallets

    @property
    def _list_view_dns(self) -> QListView:
        return self._ui.listViewDns

    @property
    def _button_search(self) -> QAbstractButton:
        return self._ui.pushButtonSearch

    @property
    def _button_exit_search(self) -> QAbstractButton:
        return self._ui.pushButtonExitSearch

    @property
    def _button_new_wallet(self) -> QPushButton:
        return self._ui.pushButtonNewWallet

    @property
    def _button_refresh_dns(self) -> QPushButton:
        return self._ui.pushButtonRefreshAll

    @property
    def _action_new_keystore(self) -> QAction:
        return self._ui.actionNewKeystore

    @property
    def _action_new_wallet(self) -> QAction:
        return self._ui.actionNew_wallet

    @property
    def _action_import_wallet_from_mnemonics(self) -> QAction:
        return self._ui.actionImportWalletFromMnemonics

    @property
    def _action_import_wallet_from_private_key(self) -> QAction:
        return self._ui.actionImport_wallet_from_private_key

    @property
    def _action_new_global_contact(self) -> QAction:
        return self._ui.actionNew_whitelist_contact

    @property
    def _action_transactions_history(self) -> QAction:
        return self._ui.action_transactions_history

    @property
    def _action_preferences(self) -> QAction:
        return self._ui.actionPreferences

    @property
    def _action_new_multiple_wallets(self) -> QAction:
        return self._ui.actionNewMultipleWallets

    @property
    def _action_backup_keystore(self) -> QAction:
        return self._ui.actionBackup_keystore

    @property
    def _action_export_keystore(self) -> QAction:
        return self._ui.actionExport_keystore_unencrypted

    @property
    def _action_import_keystore(self) -> QAction:
        return self._ui.actionImport_keystore

    @property
    def _action_quit(self) -> QAction:
        return self._ui.actionQuit

    @property
    def _action_documentation(self) -> QAction:
        return self._ui.actionDocumentation

    @property
    def _action_support(self) -> QAction:
        return self._ui.actionSupport

    @property
    def _action_shortcuts(self) -> QAction:
        return self._ui.actionShortcuts

    @property
    def _line_edit_search(self) -> QLineEdit:
        return self._ui.lineEditSearch

    @property
    def _context_menu_buttons_block(self) -> QWidget:
        return self._ui.widgetContextMenuButtons

    @property
    def _button_transfer(self) -> QPushButton:
        return self._ui.pushButtonWallets

    @property
    def _button_eye(self) -> QPushButton:
        return self._ui.pushButtonEye

    @property
    def _label_tons_version(self):
        return self._ui.tonsVersionLabel

    @property
    def _label_keystore_name(self) -> QLabel:
        return self._ui.labelKeystoreName

    @property
    def _label_balance_ton(self) -> QLabel:
        return self._ui.labelBalanceTon

    @property
    def _label_wallet_count(self) -> QLabel:
        return self._ui.labelWalletCount

    @property
    def _label_balance_fiat(self) -> QLabel:
        return self._ui.labelBalanceFiat

    @property
    def _balance_block(self) -> QWidget:
        return self._ui.balanceBlock

    @property
    def _vertical_line(self) -> QWidget:
        return self._ui.verticalLine

    @property
    def _status_bar(self) -> QStatusBar:
        return self._ui.statusBar

    @property
    def _combo_sort_by(self) -> QComboBox:
        return self._ui.comboBoxSortBy

    @property
    def _combo_dns_sort_by(self) -> QComboBox:
        return self._ui.comboBoxDnsSortBy

    @property
    def _list_view_keystores(self) -> QListView:
        return self._ui.listViewKeystores

    @property
    def _list_view_whitelists(self) -> QListView:
        return self._ui.listViewWhitelist

    @classmethod
    def _add_sidebar_item(cls, item_model: SideBarListItemModel, list_model: SideBarListModel):
        list_model.appendRow(SideBarListItem(item_model))

    def _add_keystore_item(self, keystore: SideBarListItemModel):
        self._add_sidebar_item(keystore, self._list_model_keystores)

    def _add_whitelist_item(self, whitelist: SideBarListItemModel):
        self._add_sidebar_item(whitelist, self._list_model_whitelists)

    @contextlib.contextmanager
    def _preserve_selected_keystore(self):
        current_index = self._list_view_keystores.currentIndex()
        if current_index.isValid():
            current_item = self._list_model_keystores.itemFromIndex(current_index)
            assert isinstance(current_item, SideBarListItem)
            preserved_name = current_item.item_model.name

            yield

            for row_idx in range(self._list_model_keystores.rowCount()):
                list_item = self._list_model_keystores.item(row_idx)
                assert isinstance(list_item, SideBarListItem)
                if list_item.item_model.name == preserved_name:
                    self._list_view_keystores.setCurrentIndex(self._list_model_keystores.index(row_idx, 0))
        else:
            yield

    def set_keystores(self, keystores: Sequence[SideBarListItemModel]):
        with self._preserve_selected_keystore():
            self._set_keystores_from_scratch(keystores)

    def _set_keystores_from_scratch(self, keystores: Sequence[SideBarListItemModel]):
        self._list_model_keystores.clear()
        for keystore in keystores:
            self._add_keystore_item(keystore)
        self._list_view_keystores.update()

    def notify_keystores_updated(self):
        # This works because view stores references to list items stored in model,
        # where balance is changed. use with caution, replace with QListModel modification if needed.
        # However, modifying the view model can cause the movement in the UI, which is a
        # disadvantage.
        self._list_view_keystores.update()

    @slot_exc_handler()
    def _on_backup_keystore(self, _checked: bool):
        assert self.selected_keystore_name is not None
        self._backup_keystore.emit(self.selected_keystore_name)

    @slot_exc_handler()
    def _on_export_keystore(self, _checked: bool):
        assert self.selected_keystore_name is not None
        self._export_keystore.emit(self.selected_keystore_name)

    @slot_exc_handler()
    def _on_import_keystore(self, _checked: bool):
        self._import_keystore.emit()

    def set_whitelists(self, whitelists: Sequence[SideBarListItemModel]):
        # TODO preserve (?)
        self._list_model_whitelists.clear()
        for whitelist in whitelists:
            self._add_whitelist_item(whitelist)

    def set_keystore_name(self, keystore_name: str):
        self.list_name = keystore_name

    def set_global_whitelist_name(self):
        self.list_name = "Global whitelist"

    @property
    def selected_keystore_name(self) -> typing.Optional[str]:  # TODO display it in the label instantly
        if self.selected_sidebar_item is None:
            return None
        if self.selected_sidebar_item.kind == SideBarListItemKind.password_keystore:
            return self.selected_sidebar_item.name
        elif self.selected_sidebar_item.kind == SideBarListItemKind.global_whitelist:
            return None
        else:
            raise NotImplementedError

    @property
    def selected_sidebar_item(self) -> typing.Optional[SideBarListItemModel]:
        return self._selected_sidebar_item_model

    def _install_event_filters(self):
        self._line_edit_search.installEventFilter(self)

    def set_total_balance(self, ton_balance: typing.Optional[typing.Union[Decimal, str]]):
        if ton_balance is None:
            self._balance_block.hide()
            return
        self._balance_block.show()
        balance = Decimal(ton_balance)
        self._total_balance.set(pretty_balance(balance))

        try:
            fiat_balance = balance * ton_usd_price()
        except TypeError:
            self._label_balance_fiat.hide()
        else:
            self._label_balance_fiat.show()
            self._total_balance_fiat.set(pretty_fiat_balance(fiat_balance, '$'))  # todo refactor

    def _update_balance_obscurity(self):
        # TODO fiat
        self._total_balance.set_obscure(self._sensitive_data_obscure)
        self._total_balance_fiat.set_obscure(self._sensitive_data_obscure)

    def _update_context_menu_buttons_ability(self):
        if self.selected_keystore_name is None:
            self._context_menu_buttons_block.hide()
            return

        self._context_menu_buttons_block.show()

    def _update_new_wallet_button_state(self):
        if self.selected_sidebar_item is None:
            self._button_new_wallet.setText("New wallet")
            self._button_new_wallet.setMenu(self._menu_new_wallet)
            self._button_new_wallet.setEnabled(False)
            return

        self._button_new_wallet.setEnabled(True)

        if self.selected_sidebar_item.kind == SideBarListItemKind.password_keystore:
            self._new_wallet_button_state = NewWalletButtonState.keystore
            self._button_new_wallet.setText("New wallet")
            self._button_new_wallet.setMenu(self._menu_new_wallet)
        else:
            self._new_wallet_button_state = NewWalletButtonState.global_whitelist
            self._button_new_wallet.setText("New contact")
            self._button_new_wallet.setMenu(None)

    @property
    def mouse_position(self) -> QPoint:
        return QCursor().pos()

    def notify_contact_with_name_already_exists(self, contact_name: str, location: ContactLocation):
        location_description = self._location_description(location)
        show_message_box_warning("Contact already exists",
                                 f"Contact {contact_name} already exists in {location_description}")

    def notify_contact_with_address_already_exists(self, existing_name: str, location: ContactLocation):
        location_description = self._location_description(location)
        show_message_box_warning("Contact already exists",
                                 f"Contact with same address already exists in {location_description}"
                                 f": {existing_name}")

    def notify_contact_move_empty(self):
        show_message_box_warning("Name invalid",
                                 f"Contact name should not be empty")

    def notify_record_with_name_already_exists(self, name: str, keystore_name: str):
        show_message_box_warning("Wallet already exists",
                                 f"Record {name} already exists in {keystore_name}")

    def notify_record_with_address_already_exists(self, existing_name: str, keystore_name: str):
        show_message_box_warning("Wallet already exists",
                                 f"Record with same address already exists in {keystore_name}: {existing_name}")

    def notify_record_move_empty(self):
        show_message_box_warning("Wallet name invalid", "Record name should not be empty")

    # def notify_keystores_balance_fetching(self):
    #     self._button_fetch_keystores_balance.setEnabled(False)
    #
    # def notify_keystores_balance_fetched(self):
    #     self._button_fetch_keystores_balance.setEnabled(True)

    def confirm_delete_wallet(self, wallet: WalletListItemData) -> bool:
        entity_kind = {
            WalletListItemKind.record: "wallet",
            WalletListItemKind.local_contact: "local contact",
            WalletListItemKind.global_contact: "global contact"
        }[wallet.kind]

        title = f"Delete {entity_kind}"
        message = f"Are you sure you want to delete {wallet.name}?<br>" \
                  f"This cannot be undone."
        answer = QMessageBox.question(self, title, message, defaultButton=QMessageBox.StandardButton.No)
        return answer == QMessageBox.StandardButton.Yes

    def confirm_export_keystore(self, keystore_name: str) -> bool:
        title = f"Export {keystore_name}"
        message = f"Are you sure you want to export {keystore_name}?<br>" \
                  f"This will store mnemonics in the UNENCRYPTED form."
        answer = QMessageBox.question(self, title, message, defaultButton=QMessageBox.StandardButton.No)
        return answer == QMessageBox.StandardButton.Yes

    @staticmethod
    def _location_description(location: ContactLocation) -> str:
        location_description = 'global whitelist'
        if isinstance(location, LocalWhitelistLocation):
            location_description = f"{location.keystore_name}"
        return location_description

    @staticmethod
    def _records_count(wallets: Sequence[WalletListItemData]):
        return len([wallet for wallet in wallets if wallet.kind == WalletListItemKind.record])

    def display_wallet_count(self, wallet_items: Sequence[WalletListItemData]):
        self._button_subcontext_wallets.count = self._records_count(wallet_items)

    def display_dns_count(self, count: int, all_loaded: bool):
        if not all_loaded:
            self._button_subcontext_dns.count = None
        else:
            self._button_subcontext_dns.count = count

    def update_dns_buttons_availability(self, all_loaded: bool):
        if all_loaded:
            self._button_refresh_dns.setEnabled(True)
            self._combo_dns_sort_by.setEnabled(True)
            self._dns_filter_buttons_block.setEnabled(True)
        else:
            self._button_refresh_dns.setEnabled(False)
            self._combo_dns_sort_by.setEnabled(False)
            self._dns_filter_buttons_block.setEnabled(False)

    def display_refresh_dns_menu(self, dns_menu_model: RefreshDnsMenuModel):
        self._refresh_dns_menu.display_model(dns_menu_model)

    def init_sidebar(self):
        self._list_model_keystores = SideBarListModel()
        self._list_model_whitelists = SideBarListModel()

        self._sidebar_delegate = SideBarListItemDelegate()
        for list_view in [self._list_view_keystores, self._list_view_whitelists]:
            list_view.setItemDelegate(self._sidebar_delegate)

        self._list_view_keystores.setModel(self._list_model_keystores)
        self._list_view_whitelists.setModel(self._list_model_whitelists)

    def force_select_keystore(self, keystore_name: str):
        for row_idx in range(self._list_model_keystores.rowCount()):
            list_item = self._list_model_keystores.item(row_idx)
            assert isinstance(list_item, SideBarListItem)
            if list_item.item_model.kind != SideBarListItemKind.password_keystore:
                continue
            if list_item.item_model.name == keystore_name:
                model_index = self._list_model_keystores.index(row_idx, 0)
                self._list_view_keystores.setCurrentIndex(model_index)
                self._on_keystore_selected(model_index)
                break
