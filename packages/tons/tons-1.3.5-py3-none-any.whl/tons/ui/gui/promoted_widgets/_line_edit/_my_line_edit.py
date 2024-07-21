from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QPalette
from PyQt6.QtWidgets import QLineEdit, QProxyStyle, QStyle, QWidget

from tons.ui.gui.utils import macos, windows, validation_error_color, very_valid_color, line_edit_border_color, \
    mono_font, qt_exc_handler, theme_is_dark


@lru_cache(maxsize=None)
def my_line_edit_text_left_padding() -> int:
    if macos():
        return 5
    return 0


class MyLineEditProxyStyle(QProxyStyle):
    @qt_exc_handler
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: Optional['QStyleOption'],
                      painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        assert isinstance(widget, MyLineEdit)

        if element == QStyle.PrimitiveElement.PE_PanelLineEdit:
            super().drawPrimitive(element, option, painter, widget)
            self._draw_border(option.rect, widget, painter)

    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        rect = super().subElementRect(element, option, widget)

        if element == QStyle.SubElement.SE_LineEditContents:
            rect.setX(rect.x() + my_line_edit_text_left_padding())

        return rect

    def _draw_border(self, rect: QRect, line_edit: 'MyLineEdit', painter: QPainter):
        color = self._pick_border_color(line_edit)
        width = self._pick_width(line_edit)
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
        painter.drawRect(rect)

    def _pick_border_color(self, line_edit: 'MyLineEdit') -> QColor:
        """ Very-validity has been disabled by the UX designer's will """
        # if line_edit.text_very_valid():
        #     return very_valid_color()
        if not line_edit.text_valid():
            return validation_error_color()
        elif line_edit.hasFocus():
            return self._focus_border_color(line_edit)
        else:
            return line_edit_border_color()

    def _focus_border_color(self, line_edit: 'MyLineEdit') -> QColor:
        return line_edit.palette().color(QPalette.ColorRole.Highlight)

    def _needs_colorful_border(self, line_edit: 'MyLineEdit') -> bool:
        return line_edit.hasFocus() or (not line_edit.text_valid()) or line_edit.text_very_valid()

    def _pick_width(self, line_edit: 'MyLineEdit') -> int:
        if macos():
            if self._needs_colorful_border(line_edit):
                return 4
        return 2

    def _needs_override_default_border(self, line_edit: 'MyLineEdit') -> bool:
        if macos():
            return True
        if self._needs_colorful_border(line_edit):
            return True
        return False


class MyLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(MyLineEditProxyStyle())
        if macos():
            self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)

            if theme_is_dark():
                pal = self.palette()
                pal.setColor(QPalette.ColorRole.Base, QColor(0x1c, 0x1d, 0x1f))
                self.setPalette(pal)

        self.__text_valid = True
        self.__text_very_valid = False

    def set_text_valid(self, valid: bool):
        self.__text_valid = valid

    def text_valid(self) -> bool:
        return self.__text_valid

    def set_text_very_valid(self, very_valid: bool):
        self.__text_very_valid = very_valid

    def text_very_valid(self) -> bool:
        return self.__text_very_valid

    def setStyleSheet(self, _: Optional[str]) -> None:
        assert False


class MonoLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(mono_font())
