from typing import Protocol

from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QComboBox

from tons.ui.gui.uis import CreateKeystoreUI
from tons.ui.gui.utils import TextDisplayProperty, set_text_display_valid, show_message_box_warning
from ..._base import NormalFixedSizeView
from ...components.password_input import PasswordInputViewComponent
from ...mixins.entity_name import NameView, InvalidNameNotification
from ...mixins.save_cancel_buttonbox import SaveCancelButtonBoxView


class Presenter(Protocol):
    def on_create_clicked(self): ...
    def on_password_1_edited(self): ...
    def on_password_2_edited(self): ...


class KeystoreNameView(NameView):
    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another keystore with this name already exists"
        return NameView._invalid_name_notification_text(kind)


class CreateKeystoreView(NormalFixedSizeView, KeystoreNameView, SaveCancelButtonBoxView):
    keystore_name = TextDisplayProperty('lineEditName')
    password_1 = TextDisplayProperty('lineEditPassword')
    password_2 = TextDisplayProperty('lineEditPassword_2')

    def __init__(self):
        super().__init__(CreateKeystoreUI)
        self._password_input_1 = PasswordInputViewComponent(self._eye_button_1, self._line_edit_password_1)
        self._password_input_2 = PasswordInputViewComponent(self._eye_button_2, self._line_edit_password_2)
        self.init_name_view(self._label_name_validation_error, self._line_edit_name)
        self.init_button_box(self)

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_name.setFocus()

    def setup_signals(self, presenter: Presenter):
        self._save_button.pressed.connect(presenter.on_create_clicked)
        self._line_edit_password_1.textEdited.connect(presenter.on_password_1_edited)
        self._line_edit_password_2.textEdited.connect(presenter.on_password_2_edited)

    @property
    def protection_type(self) -> str:
        return self._combo_box_protection_type.currentText()

    def hide_validation_errors(self):
        self.hide_password_validation_errors()
        self.hide_name_validation_error_notification()

    def notify_passwords_do_not_match(self, highlight: bool = False):
        self._notify_password_validation_error("Passwords do not match")
        if highlight:
            for widget in self._line_edit_password_1, self._line_edit_password_2:
                set_text_display_valid(widget, False)

    def notify_password_too_short(self, symbols: int, highlight: bool = False):
        self._notify_password_validation_error(f"Password should be at least {symbols} symbols long")
        if highlight:
            set_text_display_valid(self._line_edit_password_1, False)

    def notify_unexpected_error(self, exception: Exception):
        show_message_box_warning(title='Unexpected error',
                                 message=f'Failed to create keystore: {type(exception).__name__}')

    def hide_password_validation_errors(self):
        self._label_password_validation_error.setVisible(False)
        self.hide_password_error_highlight()

    def hide_password_error_highlight(self):
        for widget in self._line_edit_password_1, self._line_edit_password_2:
            set_text_display_valid(widget, True)

    def _notify_password_validation_error(self, text: str):
        """ For some reason, PyQt freezes the UI when displaying emojis for the first time.
        This is a problem for this window, because these notifications might be shown during editing text.
        Therefore, do not show the warning sign.
        """
        # text = " ⚠" + text
        self._label_password_validation_error.setText(text)
        self._label_password_validation_error.setVisible(True)

    @property
    def _eye_button_1(self) -> QPushButton:
        return self._ui.pushButtonEye

    @property
    def _eye_button_2(self) -> QPushButton:
        return self._ui.pushButtonEye_2

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _line_edit_password_1(self) -> QLineEdit:
        return self._ui.lineEditPassword

    @property
    def _line_edit_password_2(self) -> QLineEdit:
        return self._ui.lineEditPassword_2

    @property
    def _label_name_validation_error(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _label_password_validation_error(self) -> QLabel:
        return self._ui.labelPasswordError

    @property
    def _combo_box_protection_type(self) -> QComboBox:
        return self._ui.comboBoxProtectionType
