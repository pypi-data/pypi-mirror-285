from typing import Protocol

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QLineEdit, QPushButton, QComboBox, QLabel

from tons.ui.gui.uis import CreateContactUI
from tons.ui.gui.utils import TextDisplayProperty, set_text_display_very_valid, set_text_display_valid, \
    slot_exc_handler, ContactLocation
from .._base import NormalFixedSizeView
from ..components.entity_name import InvalidNameNotification
from tons.ui.gui.utils import TonSymbolView
from ..components.whitelists import WhitelistsViewComponent
from ..mixins.entity_name import NameView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView


class Presenter(Protocol):
    def on_user_changed_wallet_info(self): ...
    def on_show_in_scanner(self): ...
    def on_create(self): ...


class ContactNameView(NameView):
    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another contact with this name already exists"
        return NameView._invalid_name_notification_text(kind)


class CreateContactView(NormalFixedSizeView, ContactNameView, SaveCancelButtonBoxView):
    contact_name = TextDisplayProperty('lineEditName')
    address = TextDisplayProperty('lineEditAddress')
    balance = TextDisplayProperty('labelBalanceTon')
    balance_fiat = TextDisplayProperty('labelBalanceFiat')
    default_message = TextDisplayProperty('lineEditDefaultMessage')
    _mnemonics = TextDisplayProperty('plainTextEditMnemonics')

    def __init__(self):
        super().__init__(CreateContactUI)
        self.address = ''
        self.whitelists = WhitelistsViewComponent(self._combo_box_whitelists)
        self.init_name_view(self._label_name_validation_error, self._line_edit_name)
        self.init_button_box(self)
        self.ton_symbol = TonSymbolView(self._label_ton_icon)

        self._setup_signals()

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_name.setFocus()

    def _setup_signals(self):
        self.whitelists.changed.connect(self._on_location_changed)

    def setup_signals(self, presenter: Presenter):
        self._line_edit_address.textEdited.connect(presenter.on_user_changed_wallet_info)
        self._button_show_in_scanner.clicked.connect(presenter.on_show_in_scanner)
        self._save_button.clicked.connect(presenter.on_create)

    def on_top(self):
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def set_address_impressive_validity(self, very_valid: bool):
        set_text_display_very_valid(self._line_edit_address, very_valid)

    def set_address_validity(self, valid: bool):
        set_text_display_valid(self._line_edit_address, valid)

    def notify_invalid_address(self):
        self.set_address_validity(False)
        self._label_address_validation_error.setText("Invalid address")
        self._label_address_validation_error.setVisible(True)

    def notify_address_already_exists(self, name: str):
        self.set_address_validity(False)
        self._label_address_validation_error.setText(f"Contact with this address already exists: <b>{name}</b>")
        self._label_address_validation_error.setVisible(True)

    @pyqtSlot(ContactLocation)
    @slot_exc_handler()
    def _on_location_changed(self, contact_location: ContactLocation):
        self._line_edit_name.set_icon(self.whitelists.get_icon_path(contact_location))

    @property
    def _line_edit_address(self) -> QLineEdit:
        return self._ui.lineEditAddress

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _button_show_in_scanner(self) -> QPushButton:
        return self._ui.pushButtonShowInScanner

    @property
    def _combo_box_whitelists(self) -> QComboBox:
        return self._ui.comboBoxWhitelist

    @property
    def _label_name_validation_error(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _label_address_validation_error(self) -> QLabel:
        return self._ui.labelAddressValidationError

    @property
    def _label_ton_icon(self):
        return self._ui.labelTonIcon
