from functools import lru_cache, cached_property

from PyQt6.QtGui import QFont

from tons.ui.gui.utils import windows


@lru_cache
class SideBarListItemFonts:
    @cached_property
    def name(self) -> QFont:
        name = QFont()
        name.setPointSize(_name_point_size())
        return name

    @cached_property
    def balance(self) -> QFont:
        bottom = QFont()
        bottom.setPointSize(_balance_font_size())
        bottom.setWeight(_balance_font_weight())
        return bottom

    @cached_property
    def count(self) -> QFont:
        count = QFont()
        count.setPointSize(_balance_font_size())
        count.setWeight(_count_font_weight())
        return count


@lru_cache
def _balance_font_size() -> int:
    if windows():
        return 8
    return round(QFont().pointSizeF() * 11 / 13)


@lru_cache
def _count_font_size() -> int:
    if windows():
        return 8
    return round(QFont().pointSizeF() * 11 / 13)


@lru_cache
def _name_point_size() -> int:
    if windows():
        return 8
    return round(QFont().pointSize() * 14 / 13)


@lru_cache
def _balance_font_weight() -> int:
    return 700


@lru_cache
def _count_font_weight() -> int:
    return 700
