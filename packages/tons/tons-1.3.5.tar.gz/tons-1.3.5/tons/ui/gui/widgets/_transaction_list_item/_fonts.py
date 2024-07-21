from functools import cached_property, lru_cache
from typing import Sequence

from PyQt6.QtGui import QFont, QFontMetrics

from tons.ui.gui.utils import macos, mono_font_face


@lru_cache
def bottom_font_size() -> int:
    if macos():
        return 11
    return 8


@lru_cache
def top_font_size() -> int:
    return QFont().pointSize()


@lru_cache
def wallet_font_weight() -> int:
    return 700


@lru_cache
def domain_font_weight() -> int:
    return 700


@lru_cache
class TransactionFonts:
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
        dns.setWeight(domain_font_weight())
        return dns

    @cached_property
    def wallet_name(self) -> QFont:
        wallet = QFont()
        wallet.setPointSize(top_font_size())
        wallet.setWeight(domain_font_weight())
        return wallet

    @cached_property
    def top(self) -> QFont:
        top = QFont()
        top.setPointSize(top_font_size())
        return top

    @cached_property
    def address(self) -> QFont:
        return self.mono

    @cached_property
    def state(self) -> QFont:
        return self.bottom

    @cached_property
    def button(self) -> QFont:
        return self.top

    @cached_property
    def description(self) -> QFont:
        return self.top

    @cached_property
    def time(self) -> QFont:
        return self.top

    @cached_property
    def top_fonts(self) -> Sequence[QFont]:
        return TransactionFonts().domain, TransactionFonts().address, TransactionFonts().top


@lru_cache
def bottom_height() -> int:
    return QFontMetrics(TransactionFonts().state).height() + 1


@lru_cache()
def top_height() -> int:
    return max_top_ascent() + max_top_descent()


@lru_cache
def max_top_descent() -> int:
    return max(map(get_descent, TransactionFonts().top_fonts))


@lru_cache
def max_top_ascent() -> int:
    return max(map(get_ascent, TransactionFonts().top_fonts))


@lru_cache(maxsize=128)
def get_ascent(font: QFont) -> int:
    return QFontMetrics(font).ascent()


@lru_cache(maxsize=128)
def get_descent(font: QFont) -> int:
    return QFontMetrics(font).descent()


__all__ = ['TransactionFonts', 'top_height', 'bottom_height']
