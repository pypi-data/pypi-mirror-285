from functools import lru_cache

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import theme_is_dark, invert_color


@lru_cache(maxsize=None)
def gray_color() -> QColor:
    # EB EB F5 4D
    col = QColor(0xEB, 0xEB, 0xF5)
    if not theme_is_dark():
        col = invert_color(col)
    col.setAlpha(0x4D)
    return col


class SmallFatGrayLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPointSize(round(font.pointSize() * 11 / 13))
        font.setWeight(700)
        self.setFont(font)
        self.__set_palette()

    def __set_palette(self):
        palette = super().palette()
        text_color = gray_color()
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        self.setPalette(palette)
