from typing import Optional

from PyQt6 import QtCore
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPainter, QPaintEvent, QPalette, QPen, QFontMetrics, QColor
from PyQt6.QtWidgets import QSlider, QStyle, QStyleOptionSlider

from tons.ui.gui.utils import extra_small_font, qt_exc_handler


class MySlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valueChanged.connect(self.value_changed)

    def value_changed(self):  # Inside the class
        if self.value() == 0:
            self.setValue(1)

    @qt_exc_handler
    def paintEvent(self, ev: Optional[QPaintEvent]) -> None:
        p = QPainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        sr = self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, opt,
                                         QStyle.SubControl.SC_ScrollBarSlider, self)
        x, y, w, h = sr.getRect()
        c = QColor(0x31, 0x67, 0xDF, 0xFF)
        p.setBrush(c)
        c.setAlphaF(0.3)
        p.setPen(QPen(c, 2.0))
        p.drawRect(QtCore.QRect(4, y - 6, round(x * 1.95), 4))

        rect = self.geometry()

        painter = QPainter(self)
        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Text)))

        font_metrics = QFontMetrics(extra_small_font())
        font_width = font_metrics.boundingRect('12m').width()

        painter.setFont(extra_small_font())

        pos = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), 1, self.width())
        painter.drawText(QPoint(pos, rect.height()), '1m')

        pos = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), 12, self.width())
        painter.drawText(QPoint(pos - font_width, rect.height()), '12m')

        super().paintEvent(ev)
