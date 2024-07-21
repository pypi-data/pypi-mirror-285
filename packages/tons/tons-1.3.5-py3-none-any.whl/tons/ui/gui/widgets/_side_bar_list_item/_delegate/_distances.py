from functools import lru_cache, cached_property

from PyQt6.QtGui import QFontMetrics
from ._fonts import SideBarListItemFonts as _Fonts

@lru_cache
class SideBarListItemDistances:
    @cached_property
    def left_padding(self) -> int:
        return 8

    @cached_property
    def right_padding(self) -> int:
        return 0

    @cached_property
    def top_padding(self) -> int:
        return 8

    @cached_property
    def bottom_padding(self) -> int:
        return 8

    @cached_property
    def horizontal_spacing(self) -> int:
        return 8

    @cached_property
    def icon_width(self) -> int:
        return 23

    @cached_property
    def icon_height(self) -> int:
        return 17

    @cached_property
    def count_ellipse_horizontal_padding(self) -> int:
        return 6

    @cached_property
    def count_ellipse_vertical_padding(self) -> int:
        return 3

    @cached_property
    def count_ellipse_radius(self) -> int:
        return 9

    @cached_property
    def ton_symbol_width(self) -> int:
        return 9

    @cached_property
    def ton_symbol_height(self) -> int:
        return 9

    @cached_property
    def balance_symbol_spacing(self) -> int:
        # for some reason, two spaces required to return the width of one space symbol
        # calling boundingRect(' ').width() results in a value of 0
        return QFontMetrics(_Fonts().balance).boundingRect('  ').width()

    @cached_property
    def obscuring_rounded_rect_radius(self) -> int:
        return 5

    @cached_property
    def selection_rectangle_radius(self) -> int:
        return 5
