from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import QSize, Qt, QRect
from PyQt6.QtGui import QResizeEvent, QStaticText, QFont, QFontMetrics, QPainter, QColor
from PyQt6.QtWidgets import QPushButton, QStyle, QProxyStyle, QWidget, QStyleOptionButton

from tons.ui.gui.utils import macos, qt_exc_handler, theme_is_dark, invert_color


class _WalletFilterButtonMargins:
    left = 7
    right = 7


@lru_cache(maxsize=None)
def _wallet_filter_font() -> QFont:
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    font.setWeight(300)
    return font


@lru_cache
def _color_on_bevel() -> QColor:
    col = QColor(0xff,0xff,0xff,0x26)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache
def _color_sunken_bevel() -> QColor:
    col = QColor(0xff,0xff,0xff,0x52)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache
def _fixed_height() -> int:
    return 30


@lru_cache
def _rect_height() -> int:
    return 19


@lru_cache
def _rectangle_radius() -> int:
    return 5

@lru_cache
def _alpha_main_text() -> float:
    return 0.75

@lru_cache
def _alpha_count() -> float:
    return 0.30

@lru_cache
def _main_text_color() -> QColor():
    col = QColor(0xDF, 0xDE, 0xDF)
    if not theme_is_dark():
        col = invert_color(col)
    return col

@lru_cache
def _count_color() -> QColor():
    col = QColor(0xEB, 0xEB, 0xF5)
    if not theme_is_dark():
        col = invert_color(col)
    return col


def _remove_double_ampersands(src: str) -> str:
    return src.replace('&&', '&')


class WalletFilterButtonStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_PushButtonBevel:
            self._draw_bevel(option, painter)
            return

        if element == QStyle.ControlElement.CE_PushButtonLabel:
            assert isinstance(widget, WalletFilterButton)
            self._draw_text(widget, painter)
            return

        super().drawControl(element, option, painter, widget)

    def _draw_bevel(self, option: Optional['QStyleOption'], painter: QPainter):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        bevel_rect = self._true_bevel_rect(option)
        if option.state & QStyle.StateFlag.State_Sunken:
            painter.setBrush(_color_sunken_bevel())
            painter.drawRoundedRect(bevel_rect, _rectangle_radius(), _rectangle_radius())
        elif option.state & QStyle.StateFlag.State_On:
            painter.setBrush(_color_on_bevel())
            painter.drawRoundedRect(bevel_rect, _rectangle_radius(), _rectangle_radius())
        painter.restore()

    def _true_bevel_rect(self, option: QStyleOptionButton):
        paint_rect = QRect(option.rect)
        paint_rect.setHeight(_rect_height())
        paint_rect.translate(0, (option.rect.height() - _rect_height()) // 2)
        return paint_rect

    def _draw_text(self, button: 'WalletFilterButton', painter: QPainter):
        painter.save()

        static_text = QStaticText(_remove_double_ampersands(button.text()))
        x = _WalletFilterButtonMargins.left
        y = int((button.height() - static_text.size().height()) // 2) + 1
        painter.setPen(_main_text_color())
        painter.setOpacity(_alpha_main_text())
        painter.drawStaticText(x, y, static_text)

        count_static_text = QStaticText(button.count_text())
        w = int(static_text.size().width())
        painter.setPen(_count_color())
        painter.setOpacity(_alpha_count())
        painter.drawStaticText(x+w, y, count_static_text)

        painter.restore()


class WalletFilterButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count: Optional[int] = None
        self.setFont(_wallet_filter_font())
        self.__set_size()
        self.setFlat(True)
        self.setStyle(WalletFilterButtonStyle())

    def setText(self, text: Optional[str]) -> None:
        text = text or ''
        super().setText(text)
        self.__set_size()

    def set_count(self, count: Optional[int]):
        self._count = count

    def __set_size(self):
        if macos():
            self.setFixedHeight(_fixed_height())
        else:
            self.setFixedHeight(_rect_height())
        self.__set_fixed_width()
        self.parent().update()  # for an instant display, removes lag animation during window init

    @qt_exc_handler
    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.__set_size()

    def __set_fixed_width(self):
        text_size = self.text_size()
        width = (text_size.width() +
                 _WalletFilterButtonMargins.left +
                 _WalletFilterButtonMargins.right)
        self.setFixedWidth(width)

    def text_size(self) -> QSize:
        return self.__text_size(self._text())

    def main_text_size(self) -> QSize:
        return self.__text_size(self.text())

    def __text_size(self, text: str) -> QSize:
        text = _remove_double_ampersands(text)
        font_metrics = QFontMetrics(self.font())
        rect = font_metrics.boundingRect(text)
        size = QSize(rect.width(), rect.height())
        return size

    def count_text(self) -> str:
        if self._count is None:
            return ''

        return f' ({self._count})'

    def _text(self) -> str:
        return self.text() + self.count_text()

