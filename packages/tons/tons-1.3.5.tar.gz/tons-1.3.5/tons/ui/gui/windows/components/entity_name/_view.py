from enum import Enum, auto

from PyQt6.QtWidgets import QLineEdit, QLabel

from tons.ui.gui.utils import set_text_display_valid, slot_exc_handler


class InvalidNameNotification(Enum):
    empty = auto()
    exists = auto()


class NameViewComponent:
    def __init__(self, name_validation_label: QLabel, line_edit: QLineEdit):
        self._line_edit_name = line_edit
        self._name_validation_error_label = name_validation_label
        self._setup_signals()

    def _setup_signals(self):
        self._line_edit_name.textEdited.connect(self._on_name_edited)

    @slot_exc_handler
    def _on_name_edited(self, text: str):
        return
        # self.set_name_validity(text != '')

    def notify_name_validation_error(self, text: str):
        self._name_validation_error_label.setText(text)
        self._name_validation_error_label.setVisible(True)

    def hide_name_validation_error_notification_label(self):
        self._name_validation_error_label.setVisible(False)

    def hide_name_validation_error(self):
        self.set_name_validity(True)

    def set_name_validity(self, valid: bool):
        set_text_display_valid(self._line_edit_name, valid)
        if valid:
            self.hide_name_validation_error_notification_label()


__all__ = ['InvalidNameNotification',
           'NameViewComponent']
