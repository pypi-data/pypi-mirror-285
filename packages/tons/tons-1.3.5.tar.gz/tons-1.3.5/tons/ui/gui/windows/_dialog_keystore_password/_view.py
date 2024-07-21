from typing import Protocol

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, Qt

from tons.ui.gui.uis import DialogKeystorePasswordUI
from tons.ui.gui.utils import TextDisplayProperty, set_text_display_valid, slot_exc_handler
from tons.ui.gui.windows._base import DialogView
from tons.ui.gui.windows.components.password_input import PasswordInputViewComponent


class Presenter(Protocol):
    def on_password_entered(self): ...


class DialogKeystorePasswordView(DialogView):
    message = TextDisplayProperty('labelMessage')
    keystore_name = TextDisplayProperty('labelKeystoreName')
    password = TextDisplayProperty('lineEditPassword')

    def __init__(self):
        super().__init__(DialogKeystorePasswordUI)
        self._setup_signals()
        self._password_input = PasswordInputViewComponent(self._eye_button,
                                                          self._password_lineedit)

    def _setup_signals(self):
        for signal in (self._button_box.accepted, self._button_box.rejected):
            try:
                signal.disconnect()  # disable Qt Designer auto signals
            except TypeError:
                pass  # already not connected

        self._button_box.rejected.connect(self._reject)

    def setup_signals(self, presenter: Presenter):
        self._button_box.accepted.connect(presenter.on_password_entered)

    def notify_wrong_password(self):
        self.message = "Wrong password. Try again."
        self._message_label.setStyleSheet("color: red;")
        set_text_display_valid(self._password_lineedit, valid=False)
        self._password_lineedit.setFocus()

    def close_success(self):
        self.done(QtWidgets.QDialog.DialogCode.Accepted)

    @pyqtSlot()
    @slot_exc_handler()
    def _reject(self):
        self.done(QtWidgets.QDialog.DialogCode.Rejected)

    @property
    def _message_label(self) -> QtWidgets.QLabel:
        return self._ui.labelMessage

    @property
    def _password_lineedit(self) -> QtWidgets.QLineEdit:
        return self._ui.lineEditPassword

    @property
    def _eye_button(self) -> QtWidgets.QPushButton:
        return self._ui.pushButtonEye

    @property
    def _button_box(self) -> QtWidgets.QDialogButtonBox:
        return self._ui.buttonBox
