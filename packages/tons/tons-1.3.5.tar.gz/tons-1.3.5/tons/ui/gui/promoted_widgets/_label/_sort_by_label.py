from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter
from PyQt6.QtWidgets import QLabel, QProxyStyle, QStyle, QWidget

from tons.ui.gui.utils import blend_alpha, theme_is_dark, invert_color, qt_exc_handler


@lru_cache(maxsize=None)
def sort_by_font() -> QFont:
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    return font


@lru_cache(maxsize=None)
def sort_by_label_color() -> QColor:
    # EB EB F5 4D
    assert theme_is_dark()

    window_color = QPalette().color(QPalette.ColorRole.Window)
    text_color = QColor(0xEB, 0xEB, 0xF5)
    text_alpha = 0x4D / 0xFF

    return blend_alpha(window_color, text_color, text_alpha)


class SortByLabelStyle(QProxyStyle):
    @qt_exc_handler
    def drawItemText(self, painter: Optional[QPainter], rect: QRect, flags: int, pal: QPalette, enabled: bool,
                     text: Optional[str], textRole: QPalette.ColorRole = ...) -> None:
        rect.setTop(rect.top() + 2)
        super().drawItemText(painter, rect, flags, pal, enabled, text, textRole)


class SortByLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_font()
        if theme_is_dark():
            self.__set_palette()
        super().setStyle(SortByLabelStyle())

    def setFont(self, _) -> None:
        self.__set_font()

    def __set_font(self):
        super().setFont(sort_by_font())

    def __set_palette(self):
        palette = super().palette()
        text_color = sort_by_label_color()
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        self.setPalette(palette)


