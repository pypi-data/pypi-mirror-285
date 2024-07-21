from functools import lru_cache
from typing import Optional

from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import blend_alpha, theme_is_dark, invert_color, html_text_colored


@lru_cache(maxsize=None)
def _fiat_balance_font() -> QFont:
    font = QFont()
    font.setWeight(700)
    point_size = round(font.pointSize() * 11 / 13)
    font.setPointSize(point_size)
    return font


@lru_cache()
def _fiat_balance_color() -> QColor:
    # DFDEDF80 - figma
    col = QColor(0xDF, 0xDE, 0xDF, 0x80)
    if theme_is_dark():
        return col
    else:
        return invert_color(col)


@lru_cache()
def _fiat_dollar_color() -> QColor:
    """ This color is used for HTML tag which doesn't work with alpha """
    # DFDEDF4D - figma

    window_color = QPalette().color(QPalette.ColorRole.Window)
    text_color = QColor(0xDF, 0xDE, 0xDF)
    text_alpha = 0.20
    return blend_alpha(window_color, text_color, text_alpha)


class FiatBalanceLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(_fiat_balance_font())

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, _fiat_balance_color())
        self.setPalette(palette)

        self.__text = self.text()

    def text(self):
        try:
            return self.__text
        except AttributeError:
            return super().text()

    def setText(self, value: Optional[str]) -> None:
        self.__text = value
        text = self.__text
        if theme_is_dark():
            text = text.replace('$', html_text_colored('$', _fiat_dollar_color()))
        super().setText(text)

