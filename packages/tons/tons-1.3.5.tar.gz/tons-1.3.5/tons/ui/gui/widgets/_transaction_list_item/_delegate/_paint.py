from functools import lru_cache

from PyQt6.QtCore import QRect, QPoint, QLine
from PyQt6.QtGui import QPainter, QColor, QFont, QAbstractTextDocumentLayout, QPalette

from tons.ui.gui.utils import rich_text_document, RichTextElideMode, elide_rich_text, text_pixel_width, get_icon_pixmap
from tons.ui.gui.utils.animation.loaders.dash_loader import DashLoader
from tons.ui.gui.widgets._transaction_list_item._colors import TransactionColors
from tons.ui.gui.widgets._transaction_list_item._model_getters import get_state_text, get_time, get_start_time, \
    get_dash, get_end_time
from ._rectangles import TransactionRectangles
from ._sizes import TransactionDistances
from ._text_constants import cancel_button_text, get_button_text
from .._item_data import TransactionListItemData, TransactionListItemKind, TransactionButton
from .._fonts import TransactionFonts


def _draw_debug_rectangles(painter: QPainter, rectangles: TransactionRectangles):
    painter.save()

    painter.setPen(QColor(255, 0, 0))
    painter.drawRect(rectangles.status_icon)
    painter.setPen(QColor(128, 128, 0))
    painter.drawRect(rectangles.description)
    painter.setPen(QColor(0, 255, 0))
    painter.drawRect(rectangles.status)
    painter.setPen(QColor(0, 128, 128))
    painter.drawRect(rectangles.start_time)
    painter.setPen(QColor(0, 0, 240))
    painter.drawRect(rectangles.dash)
    painter.setPen(QColor(0, 0, 200))
    painter.drawRect(rectangles.end_time)
    painter.setPen(QColor(0, 0, 160))
    painter.drawRect(rectangles.button)
    painter.setPen(QColor(128, 128, 0))
    painter.drawRect(rectangles.button_icon)

    painter.setPen(QColor(0, 255, 255))
    painter.drawRect(rectangles.button_hover)

    painter.restore()


def _draw_debug_mouse_position(painter: QPainter, rectangle: QRect, local_cursor_position: QPoint):
    _draw_text(painter, TransactionFonts().mono,
               f'{rectangle.left(), rectangle.top(), local_cursor_position.x(), local_cursor_position.y()}',
               rectangle, TransactionColors().default)


def _draw_debug_frame_id(painter: QPainter, rectangle: QRect, frame_id: int):
    _draw_text(painter, TransactionFonts().mono,
               f'{frame_id=}',
               rectangle, TransactionColors().default,
               align_right=True)


def _status_icon(model: TransactionListItemData) -> str:
    return {
        TransactionListItemKind.complete: 'round_check.svg',
        TransactionListItemKind.pending: 'round_check_disabled.svg',
        TransactionListItemKind.planned: 'clock.svg',
        TransactionListItemKind.error: 'exclamation.svg'
    }[model.kind]


def _cancel_icon() -> str:
    return 'square-xmark-solid.svg'


def _cancel_icon_hover() -> str:
    return 'square-xmark-solid.svg'


def _edit_icon() -> str:
    return 'edit.svg'


def _edit_icon_hover() -> str:
    return 'edit.svg'


def _show_in_scanner_icon() -> str:
    return 'users-viewfinder-solid.svg'


def _show_in_scanner_icon_hover() -> str:
    return 'users-viewfinder-solid.svg'


def _button_icon(model: TransactionListItemData, hover: bool) -> str:
    return {
        TransactionButton.cancel: [_cancel_icon(), _cancel_icon_hover()],
        TransactionButton.edit_and_retry: [_edit_icon(), _edit_icon_hover()],
        TransactionButton.view_in_scanner: [_show_in_scanner_icon(), _show_in_scanner_icon_hover()]
    }[model.button_to_display][hover]


def _button_color(hover: bool, button_kind: TransactionButton):
    return TransactionColors().button_hover
    # if button_kind == TransactionButton.cancel:
    #     return TransactionColors().button_hover
    # return [TransactionColors().button, TransactionColors().button_hover][hover]


def draw_transaction_model_in_rectangle(painter: QPainter, rectangle: QRect, model: TransactionListItemData,
                                        local_cursor_position: QPoint,
                                        draw_debug: bool = False,
                                        need_draw_separator: bool = False,
                                        frame_id: int = 0,
                                        max_frame_id: int = 0):
    rectangles = TransactionRectangles(model, rectangle)
    if draw_debug:
        _draw_debug_rectangles(painter, rectangles)
        _draw_debug_mouse_position(painter, rectangle, local_cursor_position)
        _draw_debug_frame_id(painter, rectangle, frame_id)

    if need_draw_separator:
        _draw_separator(rectangle, rectangles, painter)

    _draw_contents(rectangles, painter, model, local_cursor_position, frame_id, max_frame_id)


def _draw_contents(rectangles: TransactionRectangles, painter: QPainter, model: TransactionListItemData,
                   local_cursor_position: QPoint, frame_id: int, max_frame_id: int):
    _draw_text(painter, TransactionFonts().description, model.description, rectangles.description,
               TransactionColors().description, elide_mode=RichTextElideMode.right)
    _draw_text(painter, TransactionFonts().state, get_state_text(model), rectangles.status, TransactionColors().status,
               elide_mode=RichTextElideMode.right)
    _draw_time(model, painter, rectangles, frame_id, max_frame_id)
    _draw_icon(painter, _status_icon(model), rectangles.status_icon)

    hover = rectangles.button_hover.contains(local_cursor_position)  # TODO force hover for 4 DNS items

    if model.button_to_display is not None:
        _draw_text(painter, TransactionFonts().button, get_button_text(model.button_to_display), rectangles.button,
                   _button_color(hover, model.button_to_display))
        _draw_icon(painter, _button_icon(model, hover), rectangles.button_icon)


def _draw_time(model: TransactionListItemData, painter: QPainter, rectangles: TransactionRectangles, frame_id: int,
               max_frame_id: int):
    _draw_text(painter, TransactionFonts().time, get_start_time(model, model.kind == TransactionListItemKind.error,
                                                                model.taken),
               rectangles.start_time, TransactionColors().time)
    _draw_dash(model, painter, rectangles, frame_id, max_frame_id)
    _draw_text(painter, TransactionFonts().time, get_end_time(model, model.kind == TransactionListItemKind.error,
                                                              model.taken),
               rectangles.end_time, TransactionColors().time)


def _draw_dash(model: TransactionListItemData, painter: QPainter, rectangles: TransactionRectangles, frame_id: int,
               max_frame_id: int):
    if not model.need_dash_animation:
        _draw_text(painter, TransactionFonts().time, get_dash(), rectangles.dash, TransactionColors().time)
    else:
        DashLoader(TransactionColors().dash_rice,
                   TransactionColors().dash,
                   TransactionDistances().dash_rice_relative_width,
                   TransactionDistances().dash_loader_relative_height,
                   TransactionDistances().dash_loader_relative_shift).paint(painter, rectangles.dash, frame_id, max_frame_id)



def _draw_separator(rectangle: QRect, rectangles: TransactionRectangles, painter: QPainter):
    painter.save()
    painter.setPen(TransactionColors().separator)
    painter.drawLine(QLine(
        QPoint(rectangles.description.left(), rectangle.top()),
        QPoint(rectangles.end_time.right(), rectangle.top())
    )
    )
    painter.restore()


def _draw_text(painter: QPainter, font: QFont, text: str, rect: QRect, color: QColor,
               elide_mode: RichTextElideMode = RichTextElideMode.center, align_right: bool = False,
               ):
    if rect.right() <= rect.left():
        return

    painter.save()
    painter.setClipRect(rect)
    text = elide_rich_text(text, rect.width(), font, elide_mode)
    td = rich_text_document(text, font)
    ctx = QAbstractTextDocumentLayout.PaintContext()
    ctx.palette.setColor(QPalette.ColorRole.Text, color)
    painter.translate(rect.topLeft())

    # if top:
    #     painter.translate(0, top_font_position_shift(font))

    if align_right:
        painter.translate(rect.width() - text_pixel_width(text, font), 0)

    td.documentLayout().draw(painter, ctx)
    painter.restore()


def _draw_icon(painter: QPainter, icon_name: str, rectangle: QRect):
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(rectangle, get_icon_pixmap(icon_name))


__all__ = ['draw_transaction_model_in_rectangle']
