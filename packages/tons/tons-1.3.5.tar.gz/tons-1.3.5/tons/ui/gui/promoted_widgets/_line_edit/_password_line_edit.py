from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QStyle, QWidget

from ._my_line_edit import MyLineEdit, MyLineEditProxyStyle
from tons.ui.gui.utils import qt_exc_handler

_EYE_BUTTON_WIDTH = 29
_EYE_BUTTON_RIGHT_MARGIN = 5


class PasswordLineEditProxyStyle(MyLineEditProxyStyle):
    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        rect = super().subElementRect(element, option, widget)

        if element == QStyle.SubElement.SE_LineEditContents:
            rect.setRight(rect.right() - _EYE_BUTTON_WIDTH - _EYE_BUTTON_RIGHT_MARGIN)

        return rect


class PasswordLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(PasswordLineEditProxyStyle())