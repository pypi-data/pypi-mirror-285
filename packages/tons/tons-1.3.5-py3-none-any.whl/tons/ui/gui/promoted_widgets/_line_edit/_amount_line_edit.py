from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPaintEvent, QPainter, QFont, QPixmap, QIcon
from PyQt6.QtWidgets import QStyle, QWidget, QStyleOption

from ._my_line_edit import MyLineEdit, MyLineEditProxyStyle
from tons.ui.gui.utils import mono_font, qt_exc_handler, get_icon, get_icon_pixmap


# TODO refactor DRY EntityNameLineEdit - make IconLineEdit


class AmountStyle(MyLineEditProxyStyle):
    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        rect = super().subElementRect(element, option, widget)

        if element == QStyle.SubElement.SE_LineEditContents:
            assert isinstance(widget, AmountLineEdit)
            delta = widget.icon_left_margin + widget.icon_bbox_width + widget.icon_right_margin
            delta -= 7
            rect.setX(rect.x() + delta)

        return rect


class AmountLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon: QIcon = get_icon('ton_symbol.svg')
        self.setStyle(AmountStyle())
        self.setFont(mono_font())

    @qt_exc_handler
    def paintEvent(self, paint_event: Optional[QPaintEvent]) -> None:
        super().paintEvent(paint_event)
        painter = QPainter(self)
        line_edit_height = self.height()
        x = int(self.icon_left_margin + (self.icon_bbox_width - self.icon_width) / 2)
        y = (line_edit_height - self.icon_height) // 2
        rect = QRect(x, y, self.icon_width, self.icon_height)
        self._icon.paint(painter, rect, mode=QIcon.Mode.Disabled)

    @property
    def icon_bbox_width(self) -> int:
        return 14

    @property
    def icon_width(self) -> int:
        return 15

    @property
    def icon_height(self) -> int:
        return 12

    @property
    def icon_left_margin(self) -> int:
        return 7

    @property
    def icon_right_margin(self) -> int:
        return 5
