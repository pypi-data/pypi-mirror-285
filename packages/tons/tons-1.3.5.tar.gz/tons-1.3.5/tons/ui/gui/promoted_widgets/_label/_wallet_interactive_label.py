from typing import Optional

from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtGui import QEnterEvent, QMouseEvent
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import qt_exc_handler


class WalletInteractiveLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_underline(True)
        self.setToolTip('Open wallet information')

    @qt_exc_handler
    def enterEvent(self, event: Optional[QEnterEvent]) -> None:
        self._set_underline(False)

    @qt_exc_handler
    def leaveEvent(self, a0: Optional[QEvent]) -> None:
        self._set_underline(True)

    def _set_underline(self, underline: bool):
        font = self.font()
        font.setUnderline(underline)
        self.setFont(font)

    @qt_exc_handler
    def mouseReleaseEvent(self, ev: Optional[QMouseEvent]) -> None:
        self.clicked.emit()

