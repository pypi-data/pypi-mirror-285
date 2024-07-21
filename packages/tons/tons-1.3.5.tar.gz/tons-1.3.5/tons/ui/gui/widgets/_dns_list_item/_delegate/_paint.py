from functools import lru_cache
from typing import Sequence

from PyQt6.QtCore import QRect, QPoint, QLine
from PyQt6.QtGui import QPainter, QColor, QFont, QAbstractTextDocumentLayout, QPalette

from tons.ui.gui.utils import rich_text_document, RichTextElideMode, elide_rich_text, text_pixel_width, get_icon_pixmap
from ._colors import Colors
from ._model_getters import get_dns_name, get_expiring_verbal_and_digits
from ._text_constants import filter_by_this_wallet, dns_visual_noise, state_text, dot_ton
from .._item_data import DnsListItemData
from ._rectangles import DnsItemRectangles
from ._fonts import Fonts, top_font_position_shift


def _draw_debug_rectangles(painter: QPainter, rectangles: DnsItemRectangles):
    painter.save()

    painter.setPen(QColor(255, 0, 0))
    painter.drawRect(rectangles.domain)
    painter.setPen(QColor(128,128,0))
    painter.drawRect(rectangles.dot_ton)
    painter.setPen(QColor(0, 255, 0))
    painter.drawRect(rectangles.wallet_name)
    painter.setPen(QColor(0, 128, 128))
    painter.drawRect(rectangles.wallet_address)
    painter.setPen(QColor(0, 0, 255))
    painter.drawRect(rectangles.expiring_verbal)
    painter.setPen(QColor(128, 128, 0))
    painter.drawRect(rectangles.expiring_digits)

    painter.setPen(QColor(0, 255, 255))
    painter.drawRect(rectangles.visual_noise)
    painter.setPen(QColor(128, 255, 255))
    painter.drawRect(rectangles.state)
    painter.setPen(QColor(255, 0, 255))
    painter.drawRect(rectangles.filter_by_this_wallet)
    painter.setPen(QColor(255,128,128))
    painter.drawRect(rectangles.icon)
    painter.setPen(QColor(255,255,255))
    painter.drawRect(rectangles.button)

    painter.restore()


def _draw_debug_mouse_position(painter: QPainter, rectangle: QRect, local_cursor_position: QPoint):
    _draw_text(painter, Fonts().mono,
               f'{rectangle.left(), rectangle.top(), local_cursor_position.x(), local_cursor_position.y()}',
               rectangle, Colors().default)


@lru_cache
def _rectangle_names_to_obscure():
    return 'domain', 'wallet_address', 'expiring_digits'


def _get_rectangles_to_obscure(rectangles: DnsItemRectangles) -> Sequence[QRect]:
    return [getattr(rectangles, rect_name) for rect_name in _rectangle_names_to_obscure()]


def _draw_obscure_rectangles(rectangles: DnsItemRectangles, painter: QPainter):
    for rectangle in _get_rectangles_to_obscure(rectangles):
        _draw_obscuring_rectangle(rectangle, painter)


def _draw_obscuring_rectangle(rectangle: QRect, painter: QPainter):
    painter.setPen(Colors().obscure_rectangle)
    painter.setBrush(Colors().obscure_rectangle)
    painter.drawRoundedRect(QRect(rectangle.left(), rectangle.top(),
                                  rectangle.width(), rectangle.height() - 2
                                  ),
                            5, 5
                            )


def _draw_skeleton(rectangles: DnsItemRectangles, painter: QPainter):
    for rect_name in rectangles.__slots__:
        rect = getattr(rectangles, rect_name)
        _draw_obscuring_rectangle(rect, painter)


def _draw_contents(rectangles: DnsItemRectangles, painter: QPainter, model: DnsListItemData,
                   local_cursor_position: QPoint, filtered_by_wallet: bool, obscure: bool):
    _draw_text(painter, Fonts().domain, dot_ton(), rectangles.dot_ton, Colors().dot_ton, True)
    _draw_text(painter, Fonts().wallet_name, model.wallet_name, rectangles.wallet_name, Colors().wallet, True)
    verbal, digits = get_expiring_verbal_and_digits(model)
    _draw_text(painter, Fonts().expires_verbal, verbal, rectangles.expiring_verbal, Colors().expiring_verbal, True)

    assert set(_rectangle_names_to_obscure()) == {'domain', 'wallet_address', 'expiring_digits'}
    if not obscure:
        _draw_text(painter, Fonts().domain, get_dns_name(model), rectangles.domain, Colors().domain, True)
        _draw_text(painter, Fonts().address, f'({model.wallet_address})', rectangles.wallet_address, Colors().address, True)
        _draw_text(painter, Fonts().expires_digits, digits, rectangles.expiring_digits, Colors().expiring_digits, True, align_right=True)

    _draw_icon(painter, 'dns_item.svg', rectangles.icon)

    mouse_hovers_over_button = rectangles.button_hover.contains(local_cursor_position)
    button_icon = 'refresh_hover.svg' if mouse_hovers_over_button else 'refresh.svg'

    _draw_icon(painter, button_icon, rectangles.button)

    if not filtered_by_wallet:
        mouse_hovers_over_filter_by_this_wallet = rectangles.filter_by_this_wallet.contains(local_cursor_position)
        filter_by_this_wallet_font = Fonts().filter_by_this_wallet_hover \
            if mouse_hovers_over_filter_by_this_wallet \
            else Fonts().filter_by_this_wallet

        _draw_text(painter, filter_by_this_wallet_font, filter_by_this_wallet(), rectangles.filter_by_this_wallet,
                   Colors().filter_by_this)
    _draw_text(painter, Fonts().state, dns_visual_noise(), rectangles.visual_noise, Colors().ton_domains_noise)
    _draw_text(painter, Fonts().state, state_text(model.kind), rectangles.state, Colors().dns_domains_status)


def draw_dns_model_in_rectangle(painter: QPainter, rectangle: QRect, model: DnsListItemData,
                                local_cursor_position: QPoint,
                                draw_debug: bool = False,
                                filtered_by_wallet: bool = False,
                                need_draw_separator: bool = False,
                                obscure: bool = False,
                                skeleton: bool = False):
    rectangles = DnsItemRectangles(model, rectangle)
    if draw_debug:
        _draw_debug_rectangles(painter, rectangles)
        _draw_debug_mouse_position(painter, rectangle, local_cursor_position)

    if need_draw_separator:
        _draw_separator(rectangle, rectangles, painter)

    if skeleton:
        _draw_skeleton(rectangles, painter)
    else:
        _draw_contents(rectangles, painter, model, local_cursor_position, filtered_by_wallet, obscure)
        if obscure:
            _draw_obscure_rectangles(rectangles, painter)


def _draw_separator(rectangle: QRect, rectangles: DnsItemRectangles, painter: QPainter):
    painter.save()
    painter.setPen(Colors().separator)
    painter.drawLine(QLine(
        QPoint(rectangles.domain.left(), rectangle.top()),
        QPoint(rectangles.expiring_digits.right(), rectangle.top())
        )
    )
    painter.restore()


def _draw_text(painter: QPainter, font: QFont, text: str, rect: QRect, color: QColor, top: bool = False,
               elide_mode: RichTextElideMode = RichTextElideMode.center, align_right: bool = False):
    if rect.right() <= rect.left():
        return

    painter.save()
    painter.setClipRect(rect)
    text = elide_rich_text(text, rect.width(), font, elide_mode)
    td = rich_text_document(text, font)
    ctx = QAbstractTextDocumentLayout.PaintContext()
    ctx.palette.setColor(QPalette.ColorRole.Text, color)
    painter.translate(rect.topLeft())

    if top:
        painter.translate(0, top_font_position_shift(font))

    if align_right:
        painter.translate(rect.width() - text_pixel_width(text, font), 0)

    td.documentLayout().draw(painter, ctx)
    painter.restore()


def _draw_icon(painter: QPainter, icon_name: str, rectangle: QRect):
    # TODO: refactor DRY
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(rectangle, get_icon_pixmap(icon_name))


__all__ = ['draw_dns_model_in_rectangle']
