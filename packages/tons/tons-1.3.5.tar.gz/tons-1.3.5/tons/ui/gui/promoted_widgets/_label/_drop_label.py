from functools import lru_cache
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QPen
from PyQt6.QtWidgets import QLabel, QProxyStyle, QStyleOptionFrame, QWidget, QFrame

from tons.ui.gui.utils import theme_is_dark, invert_color, qt_exc_handler


@lru_cache()
def _drop_pk_colour() -> QColor:
    col = QColor(0xFF, 0xFF, 0xFF, 0x26)
    if theme_is_dark():
        return col
    else:
        return invert_color(col)


@lru_cache(maxsize=None)
def _drop_pk_font() -> QFont:
    font = QFont()
    font.setWeight(500)
    # point_size = round(font.pointSize() * 11 / 13)
    # font.setPointSize(point_size)
    return font

@lru_cache
def _drop_dash_pattern() -> List[int]:
    return [2,4]

@lru_cache
def _drop_dash_width() -> int:
    return 2


class DropPkLabelStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element, option, painter, widget = ...):
        if element == QProxyStyle.ControlElement.CE_ShapedFrame:
            if widget.frameShape() != QFrame.Shape.NoFrame:
                painter.save()

                dash_pen = QPen()
                dash_pen.setColor(_drop_pk_colour())
                dash_pen.setWidth(_drop_dash_width())
                dash_pen.setDashPattern(_drop_dash_pattern())

                painter.setPen(dash_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)

                painter.drawRect(option.rect)

                painter.restore()

        else:
            return super().drawControl(element, option, painter, widget)


class DropPkLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_font()
        self._style = DropPkLabelStyle()
        self.setStyle(self._style)

    def __set_font(self):
        self.setFont(_drop_pk_font())
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, _drop_pk_colour())
        self.setPalette(palette)

    def setStyleSheet(self, _) -> None:
        assert False

    def mousePressEvent(self, ev):
        self.clicked.emit()

