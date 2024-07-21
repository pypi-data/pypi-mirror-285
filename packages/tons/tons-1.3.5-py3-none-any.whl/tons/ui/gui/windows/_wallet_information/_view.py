from typing import Protocol

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLabel, QPlainTextEdit, QLineEdit, QComboBox

from tons.ui.gui.uis import WalletInformationUI
from tons.ui.gui.utils import TextDisplayProperty, show_message_box_warning, slot_exc_handler
from ..mixins.keystore_selection import KeystoreSelectView
from ..mixins.last_activity import LastActivityView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from ..mixins.entity_name import NameView
from .._base import NormalFixedSizeView


class Presenter(Protocol):
    def on_copy_bounceable_address(self): ...
    def on_copy_nonbounceable_address(self): ...
    def on_copy_raw_address(self): ...
    def on_copy_mnemonics(self): ...
    def on_show_mnemonics_pressed(self): ...
    def on_copy_address_code(self): ...
    def on_copy_address_data(self): ...
    def on_show_qr_pressed(self): ...
    def on_viewmodel_updated(self): ...
    def on_save_clicked(self): ...
    def on_keystore_changed(self, _name: str): ...


class WalletInformationView(NormalFixedSizeView, NameView, KeystoreSelectView, SaveCancelButtonBoxView, LastActivityView):
    wallet_name = TextDisplayProperty('lineEditName')
    _balance = TextDisplayProperty('labelBalanceTon')
    balance_fiat = TextDisplayProperty('labelBalanceFiat')
    comment = TextDisplayProperty('lineEditComment')

    address_bounceable = TextDisplayProperty('lineEditAddressBounceable')
    address_nonbounceable = TextDisplayProperty('lineEditAddressNonBounceable')
    address_raw = TextDisplayProperty('lineEditAddressRaw')

    version = TextDisplayProperty('labelVersionValue')
    workchain = TextDisplayProperty('labelWorkchainValue')
    state = TextDisplayProperty('labelStateValue')
    contract_type = TextDisplayProperty('labelContractTypeValue')
    seqno = TextDisplayProperty('labelSeqnoValue')
    subwallet_id = TextDisplayProperty('labelSubwalletIdValue')

    mnemonics = TextDisplayProperty('plainTextEditMnemonics')

    def __init__(self):
        super().__init__(WalletInformationUI)
        self.init_keystore_select_view()
        self.init_name_view(self._name_validation_error_label, self._line_edit_name)
        self.init_button_box(self)

    def setup_signals(self, presenter: Presenter):
        self._ui.pushButtonShowMnemonics.clicked.connect(presenter.on_show_mnemonics_pressed)
        self._ui.pushButtonQR.clicked.connect(presenter.on_show_qr_pressed)

        """ View model changed"""
        for line_edit in (self._ui.lineEditName, self._ui.lineEditComment):
            line_edit.textEdited.connect(presenter.on_viewmodel_updated)
        self._keystore_changed.connect(presenter.on_keystore_changed)

        """ Copying """
        self._ui.pushButtonCopyBounceableAddress.clicked.connect(presenter.on_copy_bounceable_address)
        self._ui.pushButtonCopyNonBounceableAddress.clicked.connect(presenter.on_copy_nonbounceable_address)
        self._ui.pushButtonCopyRawAddress.clicked.connect(presenter.on_copy_raw_address)
        self._ui.pushButtonCopyMnemonics.clicked.connect(presenter.on_copy_mnemonics)
        self._ui.pushButtonCopySharpAddressCode.clicked.connect(presenter.on_copy_address_code)
        self._ui.pushButtonCopyAddressData.clicked.connect(presenter.on_copy_address_data)

        """ Button box """
        self._save_button.clicked.connect(presenter.on_save_clicked)

    @property
    def _label_last_activity_value_date(self) -> QLabel:
        return self._ui.labelLastActivityValueDate

    @property
    def _label_last_activity_value_time(self) -> QLabel:
        return self._ui.labelLastActivityValueTime

    def show_mnemonics(self):
        self.setUpdatesEnabled(False)
        try:
            self._ui.blockMnemonicsHidden.hide()
            self._ui.blockMnemonicsRevealed.show()
        finally:
            self.setUpdatesEnabled(True)

    @property
    def balance(self) -> str:
        return self._balance

    @balance.setter
    def balance(self, value: str):
        self._balance = value
        if not value:
            self._ui.balanceBlock.hide()
        else:
            self._ui.balanceBlock.show()

    @property
    def _line_edit_mnemonics(self) -> QPlainTextEdit:
        return self._ui.plainTextEditMnemonics

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _combo_box_keystore(self) -> QComboBox:
        return self._ui.comboBoxKeystore

    @property
    def _name_validation_error_label(self) -> QLabel:
        return self._ui.labelNameValidationError

    @pyqtSlot(int)
    @slot_exc_handler()
    def _on_combo_box_index_changed(self, current_index: int):
        KeystoreSelectView._on_combo_box_index_changed(self, current_index)

    def notify_viewmodel_different(self):
        self._save_button.setDisabled(False)

    def notify_viewmodel_unchanged(self):
        self._save_button.setDisabled(True)

    @staticmethod
    def notify_address_already_exists(name: str):
        title = "Record already exists"
        message = f"Wallet with this address already exists: \n{name}"
        show_message_box_warning(title, message)

    @staticmethod
    def notify_mnemonics_not_present():
        title = "Failed"
        message = "Mnemonics are not present for this wallet (most likely imported from a private key)"
        show_message_box_warning(title, message)

    def hide_input_error_notifications(self):
        self.hide_name_validation_error_notification()
