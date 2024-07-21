from typing import Optional

from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtWidgets import QProxyStyle, QStyle, QWidget, QToolButton, QStyleOption

from tons.ui.gui.utils import qt_exc_handler


class ShowMoreOptionsToolButtonStyle(QProxyStyle):
    @qt_exc_handler
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: Optional['QStyleOption'],
                      painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        option.rect.setX(0)
        option.rect.setY(0)
        super().drawPrimitive(element, option, painter, widget)


class ShowMoreOptionsToolButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPointSize(QFont().pointSize())
        super().setFont(font)
        self.setStyle(ShowMoreOptionsToolButtonStyle())


