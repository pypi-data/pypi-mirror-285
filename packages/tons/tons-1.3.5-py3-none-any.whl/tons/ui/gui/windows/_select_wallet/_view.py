from typing import Protocol, Dict, Optional

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QModelIndex
from PyQt6.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QWidget, QListView

from tons.ui.gui.uis import SelectWalletUI
from tons.ui.gui.utils import TextDisplayProperty, slot_exc_handler, show_message_box_warning
from tons.ui.gui.widgets import WalletListItemData, WalletListItemKind, WalletListItemDataRole
from .._base import NormalView
from ..components.contact_kind_filter import ContactKindFilterSelectViewComponent
from ..mixins.list_wallets import ListWalletsView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView


class Presenter(Protocol):
    def on_wallet_list_item_selected(self, wallet_list_item_model: WalletListItemData): ...
    def on_create_new_contact(self): ...
    def on_closed(self): ...


class SelectWalletView(NormalView, SaveCancelButtonBoxView, ListWalletsView):
    _create_new_contact = pyqtSignal()
    _wallet_selected = pyqtSignal(WalletListItemData)

    keystore_name = TextDisplayProperty('labelKeystoreName')
    wallet_count = TextDisplayProperty('labelWalletCount')

    def __init__(self):
        super().__init__(SelectWalletUI)
        self._statistics: Dict[WalletListItemKind, int] = dict()
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.contact_kind_filter = ContactKindFilterSelectViewComponent(
            self._button_all_items, self._button_keystore_wallets,
            self._button_local_whitelist, self._button_global_whitelist)
        self._setup_signals()
        self.init_button_box(self)
        self.init_list_wallets(display_transfer_arrow=False,
                               extra_hmargin=8)
        self.display_all_items_count = False

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_search.setFocus()

    def _setup_signals(self):
        self._list_view_wallets.doubleClicked.connect(self._on_list_view_wallets_double_clicked)
        self._save_button.clicked.connect(self._on_select_pressed)
        self._button_new_contact.clicked.connect(self._on_create_new_contact)

    def setup_signals(self, presenter: Presenter):
        self._wallet_selected.connect(presenter.on_wallet_list_item_selected)
        self._create_new_contact.connect(presenter.on_create_new_contact)

    def hide_new_contact_btn(self):
        self._button_new_contact.hide()

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_list_view_wallets_double_clicked(self, model_index: QModelIndex):
        wallet_data = model_index.data(WalletListItemDataRole.application_data.value)
        self._on_wallet_selected(wallet_data)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_select_pressed(self):
        self._on_wallet_selected(self.selected_wallet_model)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_create_new_contact(self):
        self._create_new_contact.emit()

    @staticmethod
    def _show_message_box_select_wallet():
        show_message_box_warning(title='No wallet selected', message='Please select a wallet')

    def _on_wallet_selected(self, wallet_data: Optional[WalletListItemData]):
        if wallet_data is None:
            self._show_message_box_select_wallet()
            return
        self.close()
        self._wallet_selected.emit(wallet_data)

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
    def _list_view_wallets(self) -> QListView:
        return self._ui.listViewWallets

    @property
    def _line_edit_search(self) -> QLineEdit:
        return self._ui.lineEditSearch

    @property
    def _combo_sort_by(self) -> QComboBox:
        return self._ui.comboBoxSortBy

    @property
    def _label_sort_by(self) -> QLabel:
        return self._ui.labelSortBy

    @property
    def _button_new_contact(self) -> QPushButton:
        return self._ui.pushButtonNew

    @property
    def _widget_filter_buttons(self) -> QWidget:
        return self._ui.widgetFilterButtons
