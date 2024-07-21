from functools import lru_cache
from math import ceil

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFontMetrics, QFont

from tons.ui.gui.utils import text_pixel_width, xstr
from ._distances import SideBarListItemDistances as _Distances
from ._fonts import SideBarListItemFonts as _Fonts
from ._format import format_balance
from ._icon import get_sidebar_icon_size
from .._item_model import SideBarListItemModel as _Model, SideBarListItemKind as _Kind, SideBarListItemKind


@lru_cache
def _name_height() -> int:
    return QFontMetrics(_Fonts().name).height() + 1


@lru_cache
def _balance_height() -> int:
    return QFontMetrics(_Fonts().balance).height() + 1


@lru_cache
def _count_height() -> int:
    return QFontMetrics(_Fonts().count).height() + 1


def _get_icon_rect_centered_in_rectangle(rect: QRect, kind: _Kind) -> QRect:
    sz = get_sidebar_icon_size(kind)
    ratio = sz.width() / sz.height()
    desired_width = ceil(rect.height() * ratio)
    return QRect(
        rect.left() + round((rect.width() - desired_width) / 2),
        rect.top(),
        desired_width,
        rect.height()
    )


@lru_cache(maxsize=1024)
def _text_pixel_width(text: str, font: QFont) -> int:
    return int(text_pixel_width(text, font) + 1)


class SideBarListItemRectangles:
    __slots__ = ['icon', 'name', 'balance', 'count', 'count_rounded_rect', 'ton_symbol']

    def __init__(self, model: _Model, rect: QRect):
        self._calculate(model, rect)

    def _calculate(self, model: _Model, rect: QRect):
        icon_bounding = QRect(
            rect.left() + _Distances().left_padding,
            rect.top() + _Distances().top_padding,
            _Distances().icon_width,
            _Distances().icon_height
        )
        self.icon = _get_icon_rect_centered_in_rectangle(icon_bounding, model.kind)
        count_width = _text_pixel_width(xstr(model.count), _Fonts().count)
        self.count = QRect(
            rect.right() - _Distances().right_padding - _Distances().count_ellipse_horizontal_padding - count_width,
            rect.top() + _Distances().top_padding + _Distances().count_ellipse_vertical_padding,
            count_width,
            _count_height()
        )
        self.count_rounded_rect = QRect(
            self.count.left() - _Distances().count_ellipse_horizontal_padding,
            self.count.top() - _Distances().count_ellipse_vertical_padding,
            self.count.width() + _Distances().count_ellipse_horizontal_padding * 2,
            self.count.height() + _Distances().count_ellipse_vertical_padding * 2
        )
        name_left = icon_bounding.right() + _Distances().horizontal_spacing
        name_right = self.count_rounded_rect.left() - _Distances().horizontal_spacing
        name_width = min(name_right - name_left, _text_pixel_width(model.name, _Fonts().name))
        self.name = QRect(
            name_left,
            rect.top() + _Distances().top_padding,
            name_width,
            _name_height()
        )
        ton_symbol_height = _Distances().ton_symbol_height if self._needs_to_be_tall(model) else 0
        ton_symbol_width = min(name_right - name_left, _Distances().ton_symbol_width)
        self.ton_symbol = QRect(
            name_left,
            self.name.bottom() + (_balance_height() - ton_symbol_height) // 2,
            ton_symbol_width,
            ton_symbol_height
        )

        self.balance = QRect(
            self.ton_symbol.right() + _Distances().balance_symbol_spacing,
            self.name.bottom(),
            min(name_right - name_left - ton_symbol_width - _Distances().balance_symbol_spacing,
                _text_pixel_width(format_balance(model.balance), _Fonts().balance)),
            _balance_height() if self._needs_to_be_tall(model) else 0
        )

    @classmethod
    def _needs_to_be_tall(cls, model: _Model) -> bool:
        return model.kind == SideBarListItemKind.password_keystore

    @classmethod
    def preferred_height(cls, model: _Model) -> int:
        central_element_height = _name_height()
        if cls._needs_to_be_tall(model):
            central_element_height += _balance_height()

        return _Distances().top_padding + central_element_height + _Distances().bottom_padding
