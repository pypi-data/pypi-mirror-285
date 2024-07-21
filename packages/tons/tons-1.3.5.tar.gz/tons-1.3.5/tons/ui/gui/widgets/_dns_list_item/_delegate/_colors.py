from functools import lru_cache, cached_property

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from tons.ui.gui.utils import theme_is_dark, invert_color
from ..._base import obscure_rectangle_color


@lru_cache
def _default_color() -> QColor:
    col = QColor(0xEB, 0xEB, 0xF5)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache(maxsize=128)
def _alpha(alpha: float) -> QColor:
    col = QColor(_default_color())
    col.setAlpha(int(0xff * alpha))
    return col


@lru_cache
class Colors:
    @cached_property
    def default(self) -> QColor:
        return _default_color()

    @cached_property
    def domain(self) -> QColor:
        return _default_color()

    @cached_property
    def dot_ton(self) -> QColor:
        return _alpha(0.4)

    @cached_property
    def wallet(self) -> QColor:
        return _default_color()

    @cached_property
    def address(self) -> QColor:
        return _alpha(0.4)

    @cached_property
    def expiring_verbal(self) -> QColor:
        return _alpha(0.25)

    @cached_property
    def expiring_digits(self) -> QColor:
        return _alpha(0.6)

    @cached_property
    def ton_domains_noise(self) -> QColor:
        return _alpha(0.4)

    @cached_property
    def dns_domains_status(self) -> QColor:
        return _alpha(0.25)

    @cached_property
    def filter_by_this(self) -> QColor:
        return _alpha(0.4)

    @cached_property
    def separator(self) -> QColor:
        return _alpha(0.07)

    @cached_property
    def obscure_rectangle(self) -> QColor:
        return obscure_rectangle_color()
