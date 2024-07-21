from functools import lru_cache
from typing import Optional

from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QProxyStyle, QStyle, QWidget, QToolButton

from tons.ui.gui.utils import qt_exc_handler, theme_is_dark, invert_color


# TODO refactor DRY (same colors in wallet filter button)

def _shade(alpha: int):
    col = QColor(0xff, 0xff, 0xff, alpha)
    if not theme_is_dark():
        col = invert_color(col)
    return col


@lru_cache
def _color_on_bevel() -> QColor:
    return _shade(0x26)


@lru_cache
def _color_sunken_bevel() -> QColor:
    return _shade(0x45)


@lru_cache
def _color_default_bevel() -> QColor:
    return _shade(0x12)


@lru_cache
def _color_bevel_border() -> QColor:
    return _shade(0x26)


@lru_cache
def _rectangle_radius() -> int:
    return 5


class SelectWalletStyle(QProxyStyle):
    @qt_exc_handler
    def drawComplexControl(self, control: QStyle.ComplexControl, option: Optional['QStyleOptionComplex'],
                           painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:

        if control == QStyle.ComplexControl.CC_ToolButton:
            pen = QPen()
            pen.setColor(_color_bevel_border())
            pen.setWidthF(1.5)
            painter.setPen(pen)

            if option.state & QStyle.StateFlag.State_Sunken:
                painter.setBrush(_color_sunken_bevel())

            elif option.state & QStyle.StateFlag.State_On:
                painter.setBrush(_color_on_bevel())

            elif option.state & QStyle.StateFlag.State_Active:
                assert isinstance(widget, SelectWalletButton)
                if widget.text() == '':  # TODO refactor better logic
                    painter.setBrush(QColor(0, 0, 0, 0))
                else:
                    painter.setBrush(_color_default_bevel())

            painter.drawRoundedRect(option.rect, _rectangle_radius(), _rectangle_radius())

            self.drawControl(QStyle.ControlElement.CE_ToolButtonLabel, option, painter, widget)

            return

        super().drawComplexControl(control, option, painter, widget)


class SelectWalletButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPointSize(QFont().pointSize())
        super().setFont(font)
        self.setStyle(SelectWalletStyle())



