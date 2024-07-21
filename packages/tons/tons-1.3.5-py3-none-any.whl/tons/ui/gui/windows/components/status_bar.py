from typing import Optional

from PyQt6.QtCore import QTimer, pyqtSlot, QObject
from PyQt6.QtWidgets import QStatusBar
from pydantic import BaseModel

from tons.ui.gui.utils import qt_exc_handler, slot_exc_handler
from tons.ui.gui.widgets.notification_bar import NotificationBar, NotificationBarMessage


class StatusBarMessageModel(BaseModel):
    message: str
    good: Optional[bool] = None


class StatusBarViewComponent(QObject):
    INTERVAL_MSEC = 5000

    def __init__(self, status_bar: NotificationBar):
        super().__init__()
        self._status_bar = status_bar
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timer_timeout)

    def display(self, message: StatusBarMessageModel):
        self._status_bar.show_message(NotificationBarMessage(text=message.message, good=message.good))
        self._set_timeout()

    def _set_timeout(self):
        self._timer.setInterval(self.INTERVAL_MSEC)
        self._timer.start()

    @pyqtSlot()
    @slot_exc_handler
    def _on_timer_timeout(self):
        self._clear()

    def _clear(self):
        self._status_bar.hide_()
