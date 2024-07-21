from functools import lru_cache, cached_property

from PyQt6.QtGui import QFont

from tons.ui.gui.utils import windows, macos, get_icon_pixmap


@lru_cache
def bottom_font_size() -> int:
    if macos():
        return 11
    if windows():
        return 8
    return round(QFont().pointSizeF() * 11 / 13)


@lru_cache
def top_font_size() -> int:
    return QFont().pointSize()


@lru_cache
def wallet_font_weight() -> int:
    return 700


@lru_cache
def top_padding() -> int:
    return 8


@lru_cache
def bottom_padding() -> int:
    return top_padding()


@lru_cache()
def left_padding() -> int:
    return 9


@lru_cache
def right_padding() -> int:
    return left_padding()


@lru_cache
def horizontal_spacing() -> int:
    return 9


@lru_cache
def icon_width() -> int:
    return 16


@lru_cache
def button_width() -> int:
    return 19


@lru_cache
def button_height() -> int:
    return 19


@lru_cache
def button_hover_margin() -> int:
    return 9


def icon_top_margin():
    return 2


@lru_cache
class DnsItemDistances:
    top_padding = top_padding()
    bottom_padding = bottom_padding()
    left_padding = left_padding()
    right_padding = right_padding()

    horizontal_spacing = horizontal_spacing()

    icon_width = icon_width()
    icon_top_margin = icon_top_margin()

    button_width = button_width()
    button_height = button_height()

    button_hover_margin = button_hover_margin()

    @cached_property
    def icon_height(self) -> int:
        pxm = get_icon_pixmap('dns_item.svg')
        return pxm.scaledToWidth(icon_width()).height()


@lru_cache
def selection_rectangle_radius() -> int:
    return 5
