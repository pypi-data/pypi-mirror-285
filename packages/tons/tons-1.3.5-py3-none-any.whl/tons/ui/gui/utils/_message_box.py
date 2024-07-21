from typing import Callable, Any, Optional

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

from tons.ui.gui.utils import set_blank_window_icon

FinishedSlot = Callable[[int], Any]


def show_message_box(title: str, message: str, icon: QMessageBox.Icon, finished_slot: Optional[FinishedSlot] = None):
    message_box = QMessageBox()
    set_blank_window_icon(message_box)
    message_box.setIcon(icon)
    message_box.setText(message)
    message_box.setWindowTitle(title)
    #  Rich text does not work properly on macOS, most likely due to a Qt bug.
    #  When displayed via static methods such as QMessageBox.question(), it at least automatically clears html tags.
    #  For the sake of simplicity, it has been decided to leave this function just show plain text on all platforms.

    # TODO further investigation: maybe replace these utility functions with static method calls and return Rich Text?
    #  However, it can lead to bugs with HTML-escaping runtime text such as wallet names.
    message_box.setTextFormat(Qt.TextFormat.PlainText)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if finished_slot is not None:
        message_box.finished.connect(finished_slot)
    message_box.exec()


def show_message_box_warning(title: str, message: str):
    icon = QMessageBox.Icon.Warning
    show_message_box(title, message, icon)


def show_message_box_critical(title: str, message: str, finished_slot: Optional[FinishedSlot] = None):
    icon = QMessageBox.Icon.Critical
    show_message_box(title, message, icon, finished_slot)

