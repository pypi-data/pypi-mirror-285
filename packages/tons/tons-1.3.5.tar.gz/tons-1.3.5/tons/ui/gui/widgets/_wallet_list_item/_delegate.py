import contextlib
from functools import lru_cache
from typing import Optional, Tuple

from PyQt6 import QtWidgets
from PyQt6.QtCore import QModelIndex, QSize, Qt, QRect, QPoint, QLine
from PyQt6.QtGui import QPainter, QFont, QStaticText, QTextOption, QColor, QPixmap, QCursor, QPalette
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QAbstractScrollArea, QListView, \
    QGraphicsBlurEffect
from tons.ui.gui.utils import theme_is_dark
from ._item_data import WalletListItemData, WalletListItemKind
from ._list_model import WalletListItemDataRole
from .._base import obscure_rectangle_color

from ...utils import xstr, gibberish, macos, remove_circle_symbols, extract_ellipse_symbol, \
    draw_state_ellipse, elide_rich_text, text_pixel_width, text_pixel_size, qt_exc_handler, invert_color, windows, \
    mono_font_face, get_icon_pixmap, get_icon_pixmap_rotated_180

_ACTIVITY_GIBBERISH_LENGTH = 4
_DEBUG_PAINT = False


@lru_cache
def _bottom_alpha() -> int:
    if theme_is_dark():
        return 0x4d
    return 0xff >> 1


@lru_cache
def _wallet_font_weight() -> int:
    return 700


@lru_cache
def _wallet_list_item_height() -> int:
    if windows():
        return 49
    return 48


@lru_cache
def _icon_width() -> int:
    return 16


@lru_cache(maxsize=128)
def _icon_height(name: str) -> int:
    return get_icon_pixmap(name).scaledToWidth(_icon_width()).height()

@lru_cache
def _hmargin() -> int:
    return 9


@lru_cache
def _hspacing() -> int:
    return _hmargin()


@lru_cache
def _vmargin() -> int:
    return _hmargin()


@lru_cache
def _bottom_font_size() -> int:
    if macos():
        return 11
    return 8


@lru_cache
def _top_font_size() -> int:
    return QFont().pointSize()


@lru_cache
def _tons_symbol_size() -> int:
    return 9


@lru_cache
def _tons_symbol_margin() -> int:
    return 7


@lru_cache
def _tons_symbol_rect_height_shift() -> int:
    return 2


@lru_cache
def arrow_size() -> int:
    return 16


@lru_cache
def arrow_rectangle_width() -> int:
    return 19


@lru_cache
def _info_spacing() -> int:
    return 10


def _get_width(widget: QAbstractScrollArea):
    return max(widget.viewport().width(), 0)


@lru_cache
def _get_mono_font():
    mono = QFont()
    mono.setFamily(mono_font_face())
    mono.setPointSize(_top_font_size())
    mono.setStyleHint(QFont.StyleHint.TypeWriter)
    return mono


@lru_cache
def _get_bottom_font() -> QFont:
    bottom = QFont()
    bottom.setPointSize(_bottom_font_size())
    return bottom


@lru_cache
def _get_wallet_name_font() -> QFont:
    wallet = QFont()
    wallet.setPointSize(_top_font_size())
    wallet.setWeight(_wallet_font_weight())
    return wallet

@lru_cache
def _selection_rectangle_radius() -> int:
    return 5


def _get_icon_name(kind: WalletListItemKind) -> str:
    matrix = {
        WalletListItemKind.record: 'wallet-solid.svg',
        WalletListItemKind.local_contact: 'contact-local.svg',
        WalletListItemKind.global_contact: 'contact-global.svg'
    }
    return matrix[kind]


class _Rectangles:
    __slots__ = 'top_left', 'top_center', 'top_right', \
                'bottom_left', 'bottom_center', 'bottom_right', \
                'icon', 'ton_symbol', 'arrow'


def _icon_top_margin() -> int:
    return 0


def __get_icon_rectangle(item_height: int, icon_name: str) -> QRect:
    y = 2 if icon_name == 'wallet-solid.svg' else 0
    return QRect(0, y, _icon_width(), _icon_height(icon_name))


def get_arrow_rectangle(width: int, height: int) -> QRect:  # no margins
    return QRect(width - arrow_rectangle_width(), 0, arrow_rectangle_width(), height)


@lru_cache
def _top_height() -> int:
    return 17


@lru_cache
def _bottom_height() -> int:
    return 14


@lru_cache
def _state_circle_gap() -> int:
    return 2


@lru_cache
def _state_circle_radius() -> int:
    return 3


@lru_cache
def _address_min_width() -> int:
    return _mono_text_pixel_width('AAABBB...CCCDDD')


@lru_cache(maxsize=1024)
def _wallet_name_pixel_width(wallet_name: str) -> int:
    return _get_text_pixel_width(wallet_name, _get_wallet_name_font())


@lru_cache(maxsize=1024)
def _mono_text_pixel_width(mono_text: str) -> int:
    return _get_text_pixel_width(mono_text, _get_mono_font())


@lru_cache(maxsize=1024)
def _bottom_text_pixel_width(bottom_text: str) -> int:
    return _get_text_pixel_width(bottom_text, _get_bottom_font())


@lru_cache(maxsize=1024)
def _get_text_pixel_width(text: str, font: QFont) -> int:
    return int(text_pixel_width(text, font) + 1)


@lru_cache(maxsize=1024)
def _get_text_pixel_size(text: str, font: QFont) -> QSize:
    size_f = text_pixel_size(text, font)
    return QSize(int(size_f.width()), int(size_f.height()))


def __get_rectangles_no_margins_only_text_and_ton_symbol(wallet_data: WalletListItemData,
                                                         width: int) -> _Rectangles:
    address_width = min(_mono_text_pixel_width(wallet_data.address), int(width * 0.4))
    balance_width = _mono_text_pixel_width(wallet_data.balance) + _tons_symbol_size() + _tons_symbol_margin()

    # Ideal widths
    address_left_x = (width - address_width) // 2
    address_right_x = address_left_x + address_width

    wallet_name_left_x = 0
    wallet_name_right_x = address_left_x - _hspacing()

    balance_left_x = width - balance_width
    balance_right_x = width

    # Compromises
    if balance_left_x - _hspacing() < address_right_x:
        address_right_x = balance_left_x - _hspacing()

    # Form rectangles
    top_height = _top_height()
    bottom_height = _bottom_height()

    rectangles = _Rectangles()

    rectangles.top_left = QRect(wallet_name_left_x, 0, wallet_name_right_x - wallet_name_left_x, top_height)
    rectangles.top_center = QRect(address_left_x, 0, address_right_x - address_left_x, top_height)
    rectangles.top_right = QRect(balance_left_x, 0, balance_right_x - balance_left_x, top_height)

    rectangles.bottom_left = rectangles.top_left.translated(0, top_height)
    rectangles.bottom_center = rectangles.top_center.translated(0, top_height)
    rectangles.bottom_right = rectangles.top_right.translated(0, top_height)

    for rectangle in [rectangles.bottom_left, rectangles.bottom_center, rectangles.bottom_right]:
        rectangle.setHeight(bottom_height)

    rectangles.ton_symbol = QRect(width - balance_width,
                                  0, _tons_symbol_size(), top_height)

    return rectangles


def __get_rectangles_no_margins(wallet_data: WalletListItemData, width: int, height: int, with_arrow: bool) -> _Rectangles:
    icon_rectangle = __get_icon_rectangle(height, _get_icon_name(wallet_data.kind))

    text_area_width = width - _icon_width() - _hspacing()

    if with_arrow:
        text_area_width -= arrow_rectangle_width() + _hspacing() * 2

    rectangles = __get_rectangles_no_margins_only_text_and_ton_symbol(wallet_data, text_area_width)

    rectangles.icon = icon_rectangle
    rectangles.arrow = get_arrow_rectangle(width, height)

    for rect_name in set(rectangles.__slots__) - {'icon', 'arrow'}:
        getattr(rectangles, rect_name).translate(rectangles.icon.width() + _hspacing(), 0)

    return rectangles


def _get_rectangles(wallet_data: WalletListItemData, width: int, height: int,
                    with_arrow: bool, extra_hmargin: int) -> _Rectangles:
    """ wallet_data: WalletListItemData without html tags (except for balance)"""

    hmargin = _hmargin() + extra_hmargin

    rectangles = __get_rectangles_no_margins(wallet_data, width - 2 * hmargin, height - 2 * _vmargin(), with_arrow)

    for rect_name in rectangles.__slots__:
        rect: QRect = getattr(rectangles, rect_name)
        rect.translate(hmargin, _vmargin())

    return rectangles


@lru_cache
def _no_wrap() -> QTextOption:
    text_option = QTextOption()
    text_option.setWrapMode(QTextOption.WrapMode.NoWrap)
    return text_option


@lru_cache
def _no_wrap_align_right() -> QTextOption:
    text_option = QTextOption(_no_wrap())
    text_option.setAlignment(Qt.AlignmentFlag.AlignRight)
    return text_option


@lru_cache(maxsize=128)
def _gibberish(length: int = 9) -> str:
    return gibberish(length)


def _get_text_position_vertically_centered_in_rectangle(rectangle: QRect, text: str, font: QFont,
                                                        align_right: bool = False) \
        -> Tuple[int, int]:
    if align_right:
        align_right = align_right
    text_size = _get_text_pixel_size(text, font)
    top_padding = (rectangle.height() - text_size.height()) // 2
    left_padding = rectangle.width() - text_size.width() if align_right else 0

    return rectangle.x() + left_padding, rectangle.y() + top_padding


_font_memo = []


def _draw_text_vertically_centered_in_rectangle(rectangle: QRect, painter: QPainter, text: str,
                                                align_right: bool = False, font: Optional[QFont] = None):
    text = elide_rich_text(text, rectangle.width(), painter.font())
    static_text = QStaticText(text)

    static_text.setTextOption(_no_wrap())

    font = font or painter.font()

    x, y = _get_text_position_vertically_centered_in_rectangle(rectangle, text, font, align_right)

    painter.setClipRect(rectangle)
    painter.drawStaticText(x, y, static_text)


def _draw_square_icon_in_bounding_rect(icon_rectangle: QRect, painter: QPainter, icon_name: str, icon_size: int,
                                       rotated_180: bool = False):
    if not rotated_180:
        pixmap = get_icon_pixmap(icon_name)
    else:
        pixmap = get_icon_pixmap_rotated_180(icon_name)

    _draw_square_pixmap_in_bounding_rect(icon_rectangle, painter, pixmap, icon_size)


def _draw_square_pixmap_in_bounding_rect(icon_rectangle: QRect, painter: QPainter, pixmap: QPixmap, icon_size: int,
                                         align_top_right: bool = False):
    if align_top_right:
        draw_icon_rect = _get_square_icon_rectangle_top_right_aligned_inside_rectangle(icon_rectangle, icon_size)
    else:
        draw_icon_rect = _get_square_icon_rectangle_centered_inside_rectangle(icon_rectangle, icon_size)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(draw_icon_rect, pixmap)


def _draw_icon_in_rectangle(rectangle: QRect, painter: QPainter, icon_name: str):
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(rectangle, get_icon_pixmap(icon_name))


@lru_cache(maxsize=128)
def _get_square_icon_rectangle_centered_inside_rectangle(rectangle: QRect, icon_size: int) -> QRect:
    icon_x = rectangle.x() + (rectangle.width() - icon_size) // 2
    icon_y = rectangle.y() + (rectangle.height() - icon_size) // 2

    return QRect(icon_x, icon_y, icon_size, icon_size)


@lru_cache(maxsize=128)
def _get_square_icon_rectangle_top_right_aligned_inside_rectangle(rectangle: QRect, icon_size: int) -> QRect:
    icon_x = rectangle.right() - icon_size
    icon_y = rectangle.top()

    return QRect(icon_x, icon_y, icon_size, icon_size)


def _get_bottom_color(painter: QPainter) -> QColor:
    col = painter.pen().color()
    col.setAlpha(_bottom_alpha())
    return col


def _draw_text_data(rectangles: _Rectangles, painter: QPainter, wallet_data: WalletListItemData, obscure: bool):

    painter.setFont(_get_wallet_name_font())

    _draw_text_vertically_centered_in_rectangle(rectangles.top_left, painter, f'{xstr(wallet_data.name)}')

    painter.setFont(_get_mono_font())

    if not obscure:
        _draw_text_vertically_centered_in_rectangle(rectangles.top_center, painter, xstr(wallet_data.address))
        _draw_text_vertically_centered_in_rectangle(rectangles.top_right, painter, xstr(wallet_data.balance),
                                                    align_right=True)

    painter.setFont(_get_bottom_font())
    painter.setPen(_get_bottom_color(painter))

    _draw_info(rectangles.bottom_left, painter, wallet_data)

    _draw_text_vertically_centered_in_rectangle(rectangles.bottom_center, painter, xstr(wallet_data.comment))
    _draw_text_vertically_centered_in_rectangle(rectangles.bottom_right, painter, xstr(wallet_data.last_activity),
                                                align_right=True)


def _draw_info(rectangle: QRect, painter: QPainter, wallet_data: WalletListItemData):
    r = QRect(rectangle)

    if wallet_data.state:
        state_text = remove_circle_symbols(wallet_data.state)
        _draw_text_vertically_centered_in_rectangle(r, painter, state_text)
        r.setX(r.x() + _bottom_text_pixel_width(state_text) + _state_circle_gap())

        symbol = extract_ellipse_symbol(wallet_data.state)
        draw_state_ellipse(symbol, r, painter, _state_circle_radius())
        r.setX(r.x() + _state_circle_radius() * 2 + _info_spacing())

    if wallet_data.version:
        _draw_text_vertically_centered_in_rectangle(r, painter, wallet_data.version)
        r.setX(r.x() + _bottom_text_pixel_width(wallet_data.version) + _info_spacing())

    if wallet_data.workchain:
        _draw_text_vertically_centered_in_rectangle(r, painter, wallet_data.workchain)


def _draw_address_obscuring_rectangle(rectangles: _Rectangles, painter: QPainter, wallet_data: WalletListItemData):
    address_x, address_y = _get_text_position_vertically_centered_in_rectangle(rectangles.top_center,
                                                                               wallet_data.address,
                                                                               _get_mono_font())
    _draw_obscuring_rectangle(
        QRect(QPoint(address_x, address_y),
              _get_text_pixel_size(wallet_data.address, _get_mono_font())),
        painter
    )


def _draw_balance_obscuring_rectangle(rectangles: _Rectangles, painter: QPainter):
    balance_x, balance_y = _get_text_position_vertically_centered_in_rectangle(rectangles.top_right,
                                                                               _gibberish(),
                                                                               _get_mono_font(),
                                                                               align_right=True)
    _draw_obscuring_rectangle(
        QRect(QPoint(balance_x, balance_y),
              _get_text_pixel_size(_gibberish(), _get_mono_font())),
        painter
    )


def _draw_activity_obscuring_rectangle(rectangles: _Rectangles, painter: QPainter):
    activity_x, activity_y = _get_text_position_vertically_centered_in_rectangle(rectangles.bottom_right,
                                                                                 _gibberish(_ACTIVITY_GIBBERISH_LENGTH),
                                                                                 _get_mono_font(),
                                                                                 align_right=True)
    _draw_obscuring_rectangle(
        QRect(QPoint(activity_x, activity_y),
              _get_text_pixel_size(_gibberish(_ACTIVITY_GIBBERISH_LENGTH), _get_mono_font())),
        painter
    )


def _draw_obscuring_rectangle(rectangle: QRect, painter: QPainter):
    painter.setPen(_obscure_rectangle_color())
    painter.setBrush(_obscure_rectangle_color())
    painter.drawRoundedRect(rectangle, 5, 5)


@contextlib.contextmanager
def _paint_context(painter: QPainter, item_view_rectangle: QRect):
    painter.save()
    painter.translate(item_view_rectangle.topLeft())
    painter.setClipRect(item_view_rectangle.translated(-item_view_rectangle.topLeft()))
    yield
    painter.restore()


@lru_cache(maxsize=None)
def _get_arrow_pixmap(wallet_kind: WalletListItemKind, hover: bool) -> QPixmap:
    if not hover:
        icon_name = 'square-arrow-up-right-solid-only-arrow.svg'
    else:
        icon_name = 'square-arrow-up-right-solid.svg'

    if wallet_kind == WalletListItemKind.record:
        return get_icon_pixmap(icon_name)
    elif wallet_kind in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:
        return get_icon_pixmap_rotated_180(icon_name)
    else:
        raise NotImplementedError


def _draw_arrow(rectangles: _Rectangles, painter: QPainter, wallet_data: WalletListItemData, hover: bool):
    pixmap = _get_arrow_pixmap(wallet_data.kind, hover)
    _draw_square_pixmap_in_bounding_rect(rectangles.arrow, painter, pixmap, arrow_size(), align_top_right=True)


@lru_cache(maxsize=128)
def _get_arrow_hover_rectangle(item_view_rectangle: QRect) -> QRect:
    width = (_hmargin() << 1) + arrow_rectangle_width()

    return QRect(
        item_view_rectangle.right() - width,
        0,
        width,
        item_view_rectangle.height()
    )


def _get_if_mouse_hovers_over_arrow(mouse_translated_pos: QPoint, item_view_rectangle: QRect) -> bool:
    hover_rectangle = _get_arrow_hover_rectangle(item_view_rectangle)
    mouse_hovers_over_arrow_rectangle = hover_rectangle.contains(mouse_translated_pos)
    return mouse_hovers_over_arrow_rectangle


def draw_model_in_rectangle(painter: QPainter, rect: QRect, wallet_data: WalletListItemData, obscure: bool = False,
                            display_transfer_arrow: bool = False, mouse_hovers_over_arrow_rectangle: bool = False,
                            need_draw_separator: bool = False, extra_hmargin: int = 0):
    rectangles = _get_rectangles(wallet_data, rect.width(), _wallet_list_item_height(), display_transfer_arrow,
                                 extra_hmargin)

    with _paint_context(painter, rect):
        _draw_text_data(rectangles, painter, wallet_data, obscure)

    with _paint_context(painter, rect):
        if _DEBUG_PAINT:
            _draw_debug_rectangles(painter, rectangles)

        _draw_icon_in_rectangle(rectangles.icon, painter, _get_icon_name(wallet_data.kind))

        if not wallet_data.last_activity:
            _draw_activity_obscuring_rectangle(rectangles, painter)

        if obscure or not wallet_data.balance:
            _draw_balance_obscuring_rectangle(rectangles, painter)

        if obscure:
            _draw_address_obscuring_rectangle(rectangles, painter, wallet_data)

        if not obscure and wallet_data.balance:
            _draw_square_icon_in_bounding_rect(rectangles.ton_symbol, painter, 'ton_symbol.svg',
                                               _tons_symbol_size())
        if display_transfer_arrow:
            _draw_arrow(rectangles, painter, wallet_data, mouse_hovers_over_arrow_rectangle)

    if need_draw_separator:
        _draw_separator(rect, painter, rectangles)


def _draw_selection_rectangle(option: QStyleOptionViewItem, painter: QPainter, item_view_rectangle: QRect):
    selection_color = option.palette.color(QPalette.ColorRole.Highlight)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(selection_color)
    painter.drawRoundedRect(item_view_rectangle, _selection_rectangle_radius(), _selection_rectangle_radius())
    painter.restore()


@lru_cache
def _separator_color() -> QColor:
    col = QColor(0xeb, 0xeb, 0xf5, int(0.07 * 0xff))
    if not theme_is_dark():
        col = invert_color(col)
    return col


def _need_draw_separator(index: QModelIndex, widget: QListView) -> bool:
    if index.row() == 0:
        return False
    try:
        return widget.selectedIndexes()[0].row() not in [index.row(), index.row() - 1]
    except (IndexError, AttributeError):
        pass
    return True


def _draw_separator(item_view_rectangle: QRect, painter: QPainter, rectangles: _Rectangles):
    painter.save()
    painter.setPen(_separator_color())
    painter.drawLine(QLine(
        QPoint(item_view_rectangle.left() + rectangles.top_left.left(), item_view_rectangle.top()),
        QPoint(item_view_rectangle.left() + rectangles.top_right.right(), item_view_rectangle.top())
        )
    )
    painter.restore()


def _draw_debug_rectangles(painter: QPainter, rectangles: _Rectangles):
    painter.save()
    painter.setPen(QColor(255, 0, 0))
    painter.drawRect(rectangles.top_left)
    painter.setPen(QColor(0, 255, 0))
    painter.drawRect(rectangles.top_center)
    painter.setPen(QColor(0, 0, 255))
    painter.drawRect(rectangles.top_right)
    painter.setPen(QColor(0, 255, 255))
    painter.drawRect(rectangles.arrow)
    painter.setPen(QColor(255, 0, 255))
    painter.drawRect(rectangles.icon)
    painter.restore()


class WalletListItemDelegate(QStyledItemDelegate):
    def __init__(self, display_transfer_arrow: bool, extra_hmargin: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._display_transfer_arrow = display_transfer_arrow
        self._extra_hmargin = extra_hmargin
        self._blur_effect = QGraphicsBlurEffect()

    @qt_exc_handler
    def paint(self, painter: Optional[QPainter], option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        options = QStyleOptionViewItem(option)

        self.initStyleOption(options, index)

        widget: QListView = option.widget
        style = widget.style()
        item_view_rectangle = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options, widget)

        if index in widget.selectedIndexes():
            _draw_selection_rectangle(option, painter, item_view_rectangle)

        wallet_data: WalletListItemData = index.data(WalletListItemDataRole.display_data.value) or \
                                          index.data(WalletListItemDataRole.application_data.value)
        if wallet_data is None:
            return

        obscure = index.data(WalletListItemDataRole.obscure.value)

        mouse_hovers_over_arrow_rectangle = _get_if_mouse_hovers_over_arrow(
                                                option.widget.viewport().mapFromGlobal(QCursor().pos()) -
                                                  item_view_rectangle.topLeft(),
                                                item_view_rectangle
                                            )

        draw_model_in_rectangle(painter, item_view_rectangle, wallet_data, obscure, self._display_transfer_arrow,
                                mouse_hovers_over_arrow_rectangle, _need_draw_separator(index, widget),
                                self._extra_hmargin)

    @qt_exc_handler
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> QSize:
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(int(_wallet_list_item_height()))
        return size_hint


@lru_cache
def _obscure_rectangle_color() -> QColor:
    return obscure_rectangle_color()


__all__ = ['WalletListItemDelegate']
