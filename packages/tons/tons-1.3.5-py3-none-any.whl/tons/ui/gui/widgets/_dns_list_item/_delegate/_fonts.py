from functools import cached_property, lru_cache
from typing import Sequence

from PyQt6.QtGui import QFont, QFontMetrics

from tons.ui.gui.utils import mono_font_face
from ._sizes import top_font_size, bottom_font_size, wallet_font_weight


@lru_cache
class Fonts:
    @cached_property
    def mono(self) -> QFont:
        mono = QFont()
        mono.setFamily(mono_font_face())
        mono.setPointSize(top_font_size())
        mono.setStyleHint(QFont.StyleHint.TypeWriter)
        return mono

    @cached_property
    def bottom(self) -> QFont:
        bottom = QFont()
        bottom.setPointSize(bottom_font_size())
        return bottom

    @cached_property
    def domain(self) -> QFont:
        dns = QFont()
        dns.setPointSize(top_font_size())
        dns.setWeight(wallet_font_weight())
        return dns

    @cached_property
    def wallet_name(self) -> QFont:
        wallet = QFont()
        wallet.setPointSize(top_font_size())
        return wallet

    @cached_property
    def expires_verbal(self) -> QFont:
        return QFont()

    @cached_property
    def expires_digits(self) -> QFont:
        return self.mono

    @cached_property
    def address(self) -> QFont:
        return self.mono

    @cached_property
    def state(self) -> QFont:
        return self.bottom

    @cached_property
    def filter_by_this_wallet(self) -> QFont:
        font = QFont(self.bottom)
        font.setUnderline(True)
        return font

    @cached_property
    def filter_by_this_wallet_hover(self) -> QFont:
        return self.bottom

    @cached_property
    def top_fonts(self) -> Sequence[QFont]:
        return Fonts().domain, Fonts().wallet_name, Fonts().address, Fonts().expires_verbal, Fonts().expires_digits

@lru_cache
def bottom_height() -> int:
    return QFontMetrics(Fonts().filter_by_this_wallet).height() + 1


@lru_cache()
def top_height() -> int:
    return max_top_ascent() + max_top_descent()


@lru_cache
def max_top_descent() -> int:
    return max(map(get_descent, Fonts().top_fonts))


@lru_cache
def max_top_ascent() -> int:
    return max(map(get_ascent, Fonts().top_fonts))


@lru_cache(maxsize=128)
def get_ascent(font: QFont) -> int:
    return QFontMetrics(font).ascent()


@lru_cache(maxsize=128)
def get_descent(font: QFont) -> int:
    return QFontMetrics(font).descent()


@lru_cache(maxsize=128)
def top_font_position_shift(font: QFont) -> int:  # TODO this functionality can be utilized not only here, refactor
    return max_top_ascent() - get_ascent(font)


__all__ = ['Fonts', 'top_font_position_shift']