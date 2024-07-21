from typing import Protocol

from PyQt6.QtWidgets import QLabel, QPlainTextEdit, QComboBox, QLineEdit

from tons.ui.gui.uis import ImportWalletFromMnemonicsUI
from tons.ui.gui.utils import TextDisplayProperty, show_message_box_warning
from .._base import NormalFixedSizeView
from ..components.entity_name import InvalidNameNotification
from tons.ui.gui.utils import TonSymbolView
from ..mixins.keystore_selection import KeystoreSelectView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from ..mixins.entity_name import NameView
from ..mixins.wallet_version_selection import WalletVersionSelectView
from ..mixins.workchain_selection import WorkchainSelectView
from ...utils import set_text_display_very_valid, set_text_display_valid


class Presenter(Protocol):
    def on_user_changed_wallet_info(self): ...
    def on_keystore_changed(self, new_name: str): ...
    def on_save_clicked(self): ...


class WalletNameView(NameView):
    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another wallet with this name already exists"
        return NameView._invalid_name_notification_text(kind)


class ImportWalletFromMnemonicsView(NormalFixedSizeView, WalletNameView, KeystoreSelectView, WalletVersionSelectView, WorkchainSelectView,
                                    SaveCancelButtonBoxView):
    wallet_name = TextDisplayProperty('lineEditName')
    balance = TextDisplayProperty('labelBalanceTon')
    balance_fiat = TextDisplayProperty('labelBalanceFiat')
    comment = TextDisplayProperty('lineEditComment')
    _mnemonics = TextDisplayProperty('plainTextEditMnemonics')

    def __init__(self):
        super().__init__(ImportWalletFromMnemonicsUI)

        self.init_name_view(self._name_validation_error_label, self._line_edit_name)
        self.init_keystore_select_view()
        self.init_button_box(self)
        self.ton_symbol = TonSymbolView(self._label_ton_icon)

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_name.setFocus()

    def setup_signals(self, presenter: Presenter):
        self._text_edit_mnemonics.textChanged.connect(presenter.on_user_changed_wallet_info)
        self._combo_box_workchain.currentTextChanged.connect(presenter.on_user_changed_wallet_info)
        self._combo_box_version.currentTextChanged.connect(presenter.on_user_changed_wallet_info)
        self._save_button.pressed.connect(presenter.on_save_clicked)
        self._keystore_changed.connect(presenter.on_keystore_changed)

        """ Button box """
        self._cancel_button.clicked.connect(self.close)

    def hide_mnemonics_validation_error_notification(self):
        self._mnemonics_validation_error_label.setVisible(False)

    @property
    def _mnemonics_validation_error_label(self) -> QLabel:
        return self._ui.labelMnemonicsValidationError

    @property
    def _text_edit_mnemonics(self) -> QPlainTextEdit:
        return self._ui.plainTextEditMnemonics

    @property
    def _combo_box_keystore(self) -> QComboBox:
        return self._ui.comboBoxKeystore

    @property
    def _combo_box_version(self) -> QComboBox:
        return self._ui.comboBoxVersion

    @property
    def _combo_box_workchain(self) -> QComboBox:
        return self._ui.comboBoxWorkchain

    @property
    def _name_validation_error_label(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _label_ton_icon(self) -> QLabel:
        return self._ui.labelTonIcon

    @property
    def mnemonics(self):
        mnemonics = self._mnemonics
        mnemonics = ' '.join(mnemonics.split())
        return mnemonics

    def set_mnemonics_impressive_validity(self, valid: bool):
        set_text_display_very_valid(self._text_edit_mnemonics, valid)
        if valid:
            self.hide_mnemonics_validation_error_notification()

    def set_mnemonics_validity(self, valid: bool):
        set_text_display_valid(self._text_edit_mnemonics, valid)
        if valid:
            self.hide_mnemonics_validation_error_notification()

    def notify_bad_mnemonics(self):
        set_text_display_valid(self._text_edit_mnemonics, False)
        self._mnemonics_validation_error_label.setVisible(True)

    @staticmethod
    def notify_address_already_exists(name: str):
        title = "Record already exists"
        message = f"Wallet with this address already exists: \n{name}"
        show_message_box_warning(title, message)


__all__ = ['ImportWalletFromMnemonicsView']


