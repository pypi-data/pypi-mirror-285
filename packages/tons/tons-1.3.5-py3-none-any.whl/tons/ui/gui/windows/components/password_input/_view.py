
from PyQt6.QtCore import pyqtSlot, QSize, QObject
from PyQt6.QtWidgets import QLineEdit, QPushButton

from tons.ui.gui.utils import slot_exc_handler, set_text_display_valid, set_icon


class PasswordInputViewComponent(QObject):
    def __init__(self, eye_button: QPushButton, line_edit: QLineEdit, become_valid_on_edit: bool = False):
        super().__init__()
        self._eye_button = eye_button
        self._password_lineedit = line_edit
        self._become_valid_on_edit = become_valid_on_edit
        self._setup_signals()
        self._hide_password()

    def _setup_signals(self):
        self._eye_button.pressed.connect(self._on_eye_clicked)
        self._password_lineedit.textEdited.connect(self._on_password_changed)

    @property
    def _password_is_hidden(self) -> bool:
        return self._password_lineedit.echoMode() == QLineEdit.EchoMode.Password

    @pyqtSlot()
    @slot_exc_handler()
    def _on_password_changed(self):
        if self._become_valid_on_edit:
            set_text_display_valid(self._password_lineedit, valid=True)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_eye_clicked(self):
        if self._password_is_hidden:
            self._show_password()
        else:
            self._hide_password()
        self._password_lineedit.setFocus()

    def _show_password(self):
        self._password_lineedit.setEchoMode(QLineEdit.EchoMode.Normal)
        set_icon(self._eye_button, 'eye-solid-78797A.svg')
        # self._eye_button.setIconSize(QSize(12, 12))

    def _hide_password(self):
        self._password_lineedit.setEchoMode(QLineEdit.EchoMode.Password)
        set_icon(self._eye_button, 'eye-slash-solid-78797A.svg')
        # self._eye_button.setIconSize(QSize(14, 14))


__all__ = ['PasswordInputViewComponent']