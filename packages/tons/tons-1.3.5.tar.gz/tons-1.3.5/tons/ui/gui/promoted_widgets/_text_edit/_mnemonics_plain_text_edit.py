from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPalette, QColor, QPainter, QPixmap, QPen
from PyQt6.QtWidgets import QPlainTextEdit, QProxyStyle, QStyleOption, QStyle, QWidget

from tons.ui.gui.utils import line_edit_border_color, macos, windows, qt_exc_handler


# TODO refactor DRY (MyLineEdit)


def _pick_border_color(widget: 'MnemonicsPlainTextEdit') -> QColor:
    if widget.hasFocus():
        return widget.palette().color(QPalette.ColorRole.Highlight)
    else:
        return line_edit_border_color()


def _needs_colorful_border(widget: 'MnemonicsPlainTextEdit') -> bool:
    return widget.hasFocus()


def _pick_width(widget: 'MnemonicsPlainTextEdit') -> int:
    if macos():
        if _needs_colorful_border(widget):
            return 4
    return 2


def _needs_override_default_border(widget: 'MnemonicsPlainTextEdit') -> bool:
    if macos():
        return True
    if _needs_colorful_border(widget):
        return True
    return False


def _draw_border(rect: QRect, widget: 'MnemonicsPlainTextEdit', painter: QPainter):
    color = _pick_border_color(widget)
    width = _pick_width(widget)
    pen = QPen(color)
    pen.setWidth(width)
    painter.setPen(pen)
    if windows():
        rect.setRight(rect.right() - 1)
        rect.setBottom(rect.bottom() - 1)
    painter.drawRect(rect)


class MnemonicsPlainTextStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        assert isinstance(widget, MnemonicsPlainTextEdit)
        if element != QStyle.ControlElement.CE_ShapedFrame or (not _needs_override_default_border(widget)):
            super().drawControl(element, option, painter, widget)
        _draw_border(option.rect, widget, painter)

    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        rect = super().subElementRect(element, option, widget)

        margin = 1

        rect.setLeft(rect.left() + margin)
        rect.setRight(rect.right() - margin)
        rect.setTop(rect.top() + margin)
        rect.setBottom(rect.bottom() - margin)

        return rect


class MnemonicsPlainTextEdit(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(MnemonicsPlainTextStyle())
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0,0,0,0))
        self.setPalette(palette)


