from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QAbstractTextDocumentLayout, QPalette

from tons.ui.gui.utils import get_icon_pixmap, RichTextElideMode, elide_rich_text, rich_text_document, xstr
from ._format import format_balance
from ._icon import get_sidebar_icon_name
from .._item_model import SideBarListItemModel as _Model
from ._rectangles import SideBarListItemRectangles as _Rectangles
from ._distances import SideBarListItemDistances as _Distances
from ._fonts import SideBarListItemFonts as _Fonts
from ._colors import SideBarListItemColors as _Colors


def _draw_debug_rectangles(painter: QPainter, rectangles: _Rectangles):
    painter.save()
    painter.setPen(QColor(0xFF, 0x00, 0x00))
    painter.drawRect(rectangles.icon)
    painter.setPen(QColor(0x00, 0xFF, 0x00))
    painter.drawRect(rectangles.name)
    painter.setPen(QColor(0x00, 0x00, 0xFF))
    painter.drawRect(rectangles.balance)
    painter.setPen(QColor(0xFF, 0xFF, 0x00))
    painter.drawRoundedRect(rectangles.count_rounded_rect,
                            _Distances().count_ellipse_radius,
                            _Distances().count_ellipse_radius)
    painter.setPen(QColor(0x00, 0xFF, 0xFF))
    painter.drawRect(rectangles.count)
    painter.setPen(QColor(0xFF, 0x00, 0xFF))
    painter.drawRect(rectangles.ton_symbol)
    painter.restore()


def draw_sidebar_model_in_rectangle(painter: QPainter, rectangle: QRect, model: _Model, selected: bool,
                                    obscure: bool, draw_debug: bool = False):
    rectangles = _Rectangles(model, rectangle)
    if draw_debug:
        _draw_debug_rectangles(painter, rectangles)

    _draw_background_rectangles(painter, rectangle, rectangles, selected)

    _draw_sidebar_icon(painter, model, rectangles)
    _draw_ton_symbol(painter, rectangles)

    _draw_name(painter, model, rectangles)
    _draw_balance(painter, model, rectangles, obscure)
    _draw_count(painter, model, rectangles, selected)


def _draw_count(painter: QPainter, model: _Model, rectangles: _Rectangles, selected: bool):
    _draw_text(painter, _Fonts().count, xstr(model.count), rectangles.count, _Colors().count(selected))


def _draw_name(painter: QPainter, model: _Model, rectangles: _Rectangles):
    _draw_text(painter, _Fonts().name, model.name, rectangles.name, _Colors().name)


def _draw_balance(painter: QPainter, model: _Model, rectangles: _Rectangles, obscure: bool):
    if not obscure:
        _draw_text(painter, _Fonts().balance, format_balance(model.balance), rectangles.balance, _Colors().balance)
    else:
        _draw_obscuring_rectangle(rectangles.balance, painter)


def _draw_obscuring_rectangle(rectangle: QRect, painter: QPainter):
    painter.setPen(_Colors().obscure_rectangle)
    painter.setBrush(_Colors().obscure_rectangle)
    painter.drawRoundedRect(rectangle,
                            _Distances().obscuring_rounded_rect_radius,
                            _Distances().obscuring_rounded_rect_radius)


def _draw_sidebar_icon(painter: QPainter, model: _Model, rectangles: _Rectangles):
    _draw_icon(painter, get_sidebar_icon_name(model.kind), rectangles.icon)


def _draw_ton_symbol(painter: QPainter, rectangles: _Rectangles):
    _draw_icon(painter, 'ton_symbol.svg', rectangles.ton_symbol)


def _draw_background_rectangles(painter: QPainter,
                                item_rectangle: QRect,
                                rectangles: _Rectangles,
                                selected: bool):
    if not selected:
        _draw_count_area_rectangle(painter, rectangles)


def _draw_count_area_rectangle(painter: QPainter, rectangles: _Rectangles):
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(_Colors().count_unselected_rounded_rect)
    painter.drawRoundedRect(rectangles.count_rounded_rect, 9, 9)


def _draw_icon(painter: QPainter, icon_name: str, rectangle: QRect):
    # TODO: refactor DRY
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(rectangle, get_icon_pixmap(icon_name))


def _draw_text(painter: QPainter, font: QFont, text: str, rect: QRect, color: QColor,
               elide_mode: RichTextElideMode = RichTextElideMode.center):
    if rect.right() <= rect.left():
        return

    painter.save()
    painter.setClipRect(rect)
    text = elide_rich_text(text, rect.width(), font, elide_mode)
    td = rich_text_document(text, font)
    ctx = QAbstractTextDocumentLayout.PaintContext()
    ctx.palette.setColor(QPalette.ColorRole.Text, color)
    painter.translate(rect.topLeft())

    td.documentLayout().draw(painter, ctx)
    painter.restore()
