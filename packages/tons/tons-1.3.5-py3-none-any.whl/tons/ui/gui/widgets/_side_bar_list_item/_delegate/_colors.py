from functools import lru_cache, cached_property

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

from tons.ui.gui.utils import theme_is_dark, invert_color
from ..._base import obscure_rectangle_color


@lru_cache
class SideBarListItemColors:
    def count(self, selected: bool) -> QColor:
        return self._selected_count if selected else self._unselected_count

    @cached_property
    def name(self) -> QColor:
        col = QColor(0xEB, 0xEB, 0xF5)
        if not theme_is_dark():
            col = invert_color(col)
        return col

    @cached_property
    def count_unselected_rounded_rect(self) -> QColor:
        col = QColor(0xFF, 0xFF, 0xFF, 0x26)
        return col

    @cached_property
    def _selected_count(self) -> QColor:
        # DFDEDF
        col = QColor(0xDF, 0xDE, 0xDF)
        if not theme_is_dark():
            return invert_color(col)
        return col

    @cached_property
    def _unselected_count(self) -> QColor:
        # DFDEDFBF
        col = QColor(0xDF, 0xDE, 0xDF, 0xDF)
        if not theme_is_dark():
            return invert_color(col)
        return col

    @cached_property
    def balance(self) -> QColor:
        # TODO DRY small fat gray label
        # EB EB F5 4D
        col = QColor(0xEB, 0xEB, 0xF5)
        if not theme_is_dark():
            col = invert_color(col)
        col.setAlpha(0x4D)
        return col

    @cached_property
    def obscure_rectangle(self) -> QColor:
        return obscure_rectangle_color()
