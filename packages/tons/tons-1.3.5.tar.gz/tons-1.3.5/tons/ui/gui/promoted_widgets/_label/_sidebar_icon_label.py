from typing import Optional

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPaintEvent, QPainter
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import qt_exc_handler


class SideBarIconLabel(QLabel):
    @qt_exc_handler
    def paintEvent(self, event: Optional[QPaintEvent]) -> None:
        pxm = self.pixmap().scaledToHeight(self.height(), mode=Qt.TransformationMode.SmoothTransformation)
        painter = QPainter(self)
        painter.drawPixmap(
            QRect(
                self.x() + (self.width() - pxm.width()) // 2,
                self.y(),
                pxm.width(),
                pxm.height()
            ),
            pxm
        )
