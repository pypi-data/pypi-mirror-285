from functools import lru_cache, cached_property

from PyQt6.QtGui import QColor

from tons.ui.gui.utils import theme_is_dark, invert_color


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
def _red() -> QColor:
    #ED6A5F
    return QColor(0xED, 0x6A, 0x5F)


@lru_cache(maxsize=128)
def _red_alpha(alpha: float) -> QColor:
    col = QColor(_red())
    col.setAlpha(int(0xff * alpha))
    return col


@lru_cache
class TransactionColors:
    @cached_property
    def description(self) -> QColor:
        return _alpha(0.66)

    @cached_property
    def button(self) -> QColor:
        return _alpha(0.15)

    @cached_property
    def button_hover(self) -> QColor:
        return _alpha(0.66)

    @cached_property
    def highlight(self) -> QColor:
        return _default_color()

    @cached_property
    def default(self) -> QColor:
        return _alpha(0.66)

    @cached_property
    def status(self) -> QColor:
        return _alpha(0.15)

    @cached_property
    def error(self) -> QColor:
        return _red()

    @cached_property
    def error_seconds(self) -> QColor:
        return _red_alpha(0.15)

    @cached_property
    def error_pending(self) -> QColor:
        return _red_alpha(0.15)

    @cached_property
    def dot_ton(self) -> QColor:
        return _alpha(0.30)

    @cached_property
    def seconds(self) -> QColor:
        return _alpha(0.15)

    @cached_property
    def time(self) -> QColor:
        return _alpha(0.66)

    @cached_property
    def pending_time(self) -> QColor:
        return _alpha(0.15)

    @cached_property
    def dash(self) -> QColor:
        return _alpha(0.15)

    @cached_property
    def dash_rice(self) -> QColor:
        return _alpha(1.00)

    @cached_property
    def separator(self) -> QColor:
        return _alpha(0.07)

__all__ = ['TransactionColors']
