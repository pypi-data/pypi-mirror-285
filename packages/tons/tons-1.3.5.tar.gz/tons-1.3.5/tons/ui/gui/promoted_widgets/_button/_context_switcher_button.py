from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QResizeEvent, QStaticText, QFont, QFontMetrics, QPainter, QColor, QTextDocument, \
    QPalette
from PyQt6.QtWidgets import QPushButton, QStyle, QProxyStyle, QWidget, QStyleOptionButton

from tons.ui.gui.utils import qt_exc_handler, theme_is_dark, invert_color, blended_text_color, dashstr


# TODO: refactor DRY (WalletFilterButton, flat push button)


class _ContextSwitcherButtonMargins:
    left = 7
    right = 7
    line_spacing = 1


@lru_cache(maxsize=None)
def _context_switcher_caption_font() -> QFont:
    font = QFont()
    font.setWeight(700)
    return font


@lru_cache(maxsize=None)
def _context_switcher_counter_font() -> QFont:
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    return font


@lru_cache
def _color_on_bevel() -> QColor:
    col = QColor(0xff, 0xff, 0xff, 0x26)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache
def _color_sunken_bevel() -> QColor:
    col = QColor(0xff, 0xff, 0xff, 0x52)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache
def _rect_height() -> int:
    return 30


@lru_cache
def _rectangle_radius() -> int:
    return 5


@lru_cache
def _caption_color() -> QColor:
    return QPalette().color(QPalette.ColorRole.WindowText)


@lru_cache
def _counter_color() -> QColor:
    return blended_text_color(0.5, background_role=QPalette.ColorRole.Base)


@lru_cache
def _caption_bounding_rect(caption: str) -> QRect:
    return QFontMetrics(_context_switcher_caption_font()).boundingRect(caption)


@lru_cache
def _caption_width(caption: str) -> int:
    return _caption_bounding_rect(caption).width()


@lru_cache(maxsize=256)
def _counter_bounding_rect(count: Optional[int]) -> QRect:
    return QFontMetrics(_context_switcher_counter_font()).boundingRect(dashstr(count))


@lru_cache(maxsize=256)
def _counter_width(count: Optional[int]) -> int:
    return _counter_bounding_rect(count).width()


class _ContextSwitcherButtonStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_PushButtonBevel:

            painter.setPen(Qt.PenStyle.NoPen)
            bevel_rect = self._true_bevel_rect(option)

            if option.state & QStyle.StateFlag.State_Sunken:
                painter.setBrush(_color_sunken_bevel())
                painter.drawRoundedRect(bevel_rect, _rectangle_radius(), _rectangle_radius())

            elif option.state & QStyle.StateFlag.State_On:
                painter.setBrush(_color_on_bevel())
                painter.drawRoundedRect(bevel_rect, _rectangle_radius(), _rectangle_radius())

            return

        if element == QStyle.ControlElement.CE_PushButtonLabel and \
                isinstance(option, QStyleOptionButton) and \
                isinstance(widget, ContextSwitcherButton):

            rectangles = _ContextSwitcherRectangles(widget.caption, widget.count, option.rect)

            painter.setPen(_caption_color())
            painter.setFont(_context_switcher_caption_font())
            painter.drawStaticText(rectangles.caption.topLeft(), QStaticText(widget.caption))

            painter.setPen(_counter_color())
            painter.setFont(_context_switcher_counter_font())
            painter.drawStaticText(rectangles.count.topLeft(), QStaticText(dashstr(widget.count)))

            return

        super().drawControl(element, option, painter, widget)

    def _true_bevel_rect(self, option: QStyleOptionButton):
        paint_rect = QRect(option.rect)
        paint_rect.setHeight(_rect_height())
        paint_rect.translate(0, (option.rect.height() - _rect_height()) // 2)
        return paint_rect


class _ContextSwitcherRectangles:
    __slots__ = ['caption', 'count']

    def __init__(self, caption: str, count: Optional[int], item_rect: QRect):
        caption_bounding_rect = _caption_bounding_rect(caption)
        count_bounding_rect = _counter_bounding_rect(count)
        total_height = caption_bounding_rect.height() + _ContextSwitcherButtonMargins.line_spacing + count_bounding_rect.height()
        vertical_margin = (item_rect.height() - total_height) // 2

        self.caption = QRect(
            item_rect.left() + (item_rect.width() - caption_bounding_rect.width()) // 2,
            item_rect.top() + vertical_margin,
            caption_bounding_rect.width(),
            caption_bounding_rect.height()
        )

        self.count = QRect(
            item_rect.left() + (item_rect.width() - count_bounding_rect.width()) // 2,
            item_rect.top() + vertical_margin + self.caption.height() + _ContextSwitcherButtonMargins.line_spacing,
            count_bounding_rect.width(),
            count_bounding_rect.height()
        )


class ContextSwitcherButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._count: Optional[int] = None
        self._document: Optional[QTextDocument] = None

        self.__set_size()
        self.setFlat(True)
        self.setStyle(_ContextSwitcherButtonStyle())

    @property
    def caption(self) -> str:
        return self.text()

    @property
    def count(self) -> Optional[int]:
        return self._count

    @count.setter
    def count(self, value: Optional[int]):
        self._count = value
        self.repaint()

    @property
    def document(self) -> QTextDocument:
        return self._document

    def setText(self, text: Optional[str]) -> None:
        text = text or ''
        super().setText(text)
        self.__set_size()

    def __set_size(self):
        self.__set_fixed_width()
        self.parent().update()  # for an instant display, removes lag animation during window init

    @qt_exc_handler
    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.__set_size()

    def __set_fixed_width(self):
        width = (max(_caption_width(self.caption), _counter_width(self._count)) +
                 _ContextSwitcherButtonMargins.left +
                 _ContextSwitcherButtonMargins.right)
        self.setFixedWidth(width)

