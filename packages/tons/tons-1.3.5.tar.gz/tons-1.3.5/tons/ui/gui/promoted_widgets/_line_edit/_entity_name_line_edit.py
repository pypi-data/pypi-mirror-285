from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPaintEvent, QPainter, QFont, QPixmap
from PyQt6.QtWidgets import QStyle, QWidget, QStyleOption

from ._my_line_edit import MyLineEdit, MyLineEditProxyStyle
from tons.ui.gui.utils import qt_exc_handler, get_icon_pixmap


class EntityNameProxyStyle(MyLineEditProxyStyle):
    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        rect = super().subElementRect(element, option, widget)

        if element == QStyle.SubElement.SE_LineEditContents:
            assert isinstance(widget, EntityNameLineEdit)
            delta = widget.icon_left_margin + widget.icon_bbox_width + widget.icon_right_margin
            delta -= 7
            rect.setX(rect.x() + delta)

        return rect


class EntityNameLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon_pixmap: Optional[QPixmap] = None

        self.setStyle(EntityNameProxyStyle())
        self._setup_font()

    def _setup_font(self):
        font = self.font()
        font.setWeight(QFont.Weight.DemiBold)
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)

    def set_icon(self, icon_name: str):
        self._icon_pixmap = get_icon_pixmap(icon_name)
        self.repaint()

    @qt_exc_handler
    def paintEvent(self, paint_event: Optional[QPaintEvent]) -> None:
        super().paintEvent(paint_event)
        painter = QPainter(self)
        line_edit_height = self.height()
        x = int(self.icon_left_margin + (self.icon_bbox_width - self.icon_width) / 2)
        y = (line_edit_height - self.icon_height) // 2
        rect = QRect(x, y, self.icon_width, self.icon_height)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(rect, self._icon_pixmap)

    @property
    def icon_bbox_width(self) -> int:
        return 23

    @property
    def icon_width(self) -> int:
        return 16

    @property
    def icon_height(self) -> int:
        return int(self.icon_width / self._icon_pixmap.width() * self._icon_pixmap.height() + 1)

    @property
    def icon_left_margin(self) -> int:
        return 7

    @property
    def icon_right_margin(self) -> int:
        return 7


class KeystoreNameLineEdit(EntityNameLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_icon('lock-solid.svg')

    @property
    def icon_width(self) -> int:
        return 9


class WalletNameLineEdit(EntityNameLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_icon('wallet-solid.svg')

    @property
    def icon_bbox_width(self) -> int:
        return 16

    @property
    def icon_width(self) -> int:
        return 14


class ContactNameLineEdit(EntityNameLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_icon('contact.svg')

    @property
    def icon_bbox_width(self) -> int:
        return 16

    @property
    def icon_width(self) -> int:
        return 16


class WalletPatternNameLineEdit(EntityNameLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_icon('wallet-solid.svg')

    def _setup_font(self):
        pass

    @property
    def icon_bbox_width(self) -> int:
        return 16
