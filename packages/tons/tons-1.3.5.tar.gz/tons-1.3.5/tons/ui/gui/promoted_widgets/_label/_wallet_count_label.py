from functools import lru_cache

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import theme_is_dark, invert_color


@lru_cache()
def _wallet_count_color() -> QColor:
    # DFDEDF80 - figma
    col = QColor(0xDF, 0xDE, 0xDF, 0x80)
    if theme_is_dark():
        return col
    else:
        return invert_color(col)


@lru_cache(maxsize=None)
def _wallet_count_font() -> QFont:
    font = QFont()
    font.setWeight(700)
    point_size = round(font.pointSize() * 11 / 13)
    font.setPointSize(point_size)
    return font


class WalletCountLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_font()

    def __set_font(self):
        self.setFont(_wallet_count_font())
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, _wallet_count_color())
        self.setPalette(palette)

    def setStyleSheet(self, _) -> None:
        assert False
