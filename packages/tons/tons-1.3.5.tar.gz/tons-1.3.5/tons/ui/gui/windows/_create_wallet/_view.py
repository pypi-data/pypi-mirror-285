from typing import Protocol

from PyQt6.QtWidgets import QLabel, QComboBox, QLineEdit

from tons.ui.gui.uis import CreateWalletUI
from tons.ui.gui.utils import TextDisplayProperty, show_message_box_warning
from .._base import NormalFixedSizeView
from ..components.entity_name import InvalidNameNotification
from ..mixins.keystore_selection import KeystoreSelectView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from ..mixins.entity_name import NameView
from ..mixins.wallet_version_selection import WalletVersionSelectView
from ..mixins.workchain_selection import WorkchainSelectView


class Presenter(Protocol):
    def on_keystore_changed(self, new_name: str): ...
    def on_save_clicked(self): ...


class WalletNameView(NameView):
    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another wallet with this name already exists"
        return NameView._invalid_name_notification_text(kind)


class CreateWalletView(NormalFixedSizeView, WalletNameView, KeystoreSelectView, WalletVersionSelectView, WorkchainSelectView,
                       SaveCancelButtonBoxView):
    wallet_name = TextDisplayProperty('lineEditName')
    comment = TextDisplayProperty('lineEditComment')

    def __init__(self):
        super().__init__(CreateWalletUI)
        self.init_name_view(self._name_validation_error_label, self._line_edit_name)
        self.init_keystore_select_view()
        self.init_button_box(self)

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_name.setFocus()

    def setup_signals(self, presenter: Presenter):
        self._save_button.pressed.connect(presenter.on_save_clicked)
        self._keystore_changed.connect(presenter.on_keystore_changed)

        """ Button box """
        self._cancel_button.clicked.connect(self.close)


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

    @staticmethod
    def notify_address_already_exists(name: str):
        title = "Record already exists"
        message = f"Wallet with this address already exists: \n{name}"
        show_message_box_warning(title, message)


__all__ = ['CreateWalletView']


