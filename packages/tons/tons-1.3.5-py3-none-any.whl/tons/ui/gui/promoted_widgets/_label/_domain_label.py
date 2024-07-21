from functools import lru_cache, cached_property
from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPaintEvent, QPainter
from PyQt6.QtWidgets import QProxyStyle

from ._demi_bold_label import Weight700Label
from ...utils import html_text_colored, qt_exc_handler


@lru_cache
def _domain_font_size() -> int:
    font = QFont()
    return round(font.pointSize() * 14 / 13)


@lru_cache
def _dot_ton_alpha() -> float:
    return 0.30

@lru_cache
def _ton_icon_size() -> int:
    return 16

@lru_cache
def _ton_icon_margin() -> int:
    return 0


class DomainLabel(Weight700Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._domain: Optional[str] = None

        font = self.font()
        font.setPointSize(_domain_font_size())
        self.setFont(font)

    @cached_property
    def _don_ton_color(self) -> QColor:
        col = self.palette().color(QPalette.ColorRole.Text)
        col.setAlphaF(_dot_ton_alpha())
        return col

    @property
    def domain(self) -> Optional[str]:
        return self._domain

    @domain.setter
    def domain(self, value: str):
        self._domain = value
        self.__set_domain()

    def __set_domain(self):
        text = self._domain
        text += html_text_colored('.ton', self._don_ton_color)
        self.setText(text)
        self.repaint()


__all__ = ['DomainLabel']
