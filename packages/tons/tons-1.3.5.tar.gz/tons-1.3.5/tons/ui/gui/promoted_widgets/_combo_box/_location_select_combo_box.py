from typing import Optional

from PyQt6.QtCore import QRect, QPointF
from PyQt6.QtGui import QPainter, QStaticText
from PyQt6.QtWidgets import QComboBox, QProxyStyle, QStyle, QWidget, QStyleOptionComplex, QStyleOptionComboBox, \
    QStyleOption

from tons.ui.gui.utils import qt_exc_handler


class LocationSelectStyle(QProxyStyle):
    box_height = 17
    spacing = 7

    @qt_exc_handler
    def drawComplexControl(self, control: QStyle.ComplexControl,
                           option: Optional['QStyleOptionComplex'], painter: Optional[QPainter],
                           widget: Optional[QWidget] = ...) -> None:
        return

    @qt_exc_handler
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: Optional['QStyleOption'],
                      painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        super().drawPrimitive(element, option, painter, widget)

    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_ComboBoxLabel:

            assert isinstance(option, QStyleOptionComboBox)

            icon = option.currentIcon

            icon_rect = QRect(
                0,
                (option.rect.height() - self.box_height) // 2,
                16,
                self.box_height
            )

            icon.paint(painter, icon_rect)

            static_text = QStaticText(option.currentText)

            text_pos = QPointF(
                icon_rect.right() + self.spacing,
                (option.rect.height() - static_text.size().height()) / 2
            )

            painter.drawStaticText(text_pos, static_text)

            arrow_option = QStyleOption()
            aw = 8
            ah = 8
            ax = int(text_pos.x() + static_text.size().width() + self.spacing)
            ay = int(option.rect.top() + (option.rect.height() - ah) // 2)

            arrow_option.rect = QRect(ax, ay, aw, ah)
            super().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorArrowDown, arrow_option, painter, None)

            return

        return super().drawControl(element, option, painter, widget)


class LocationSelectComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(LocationSelectStyle())
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
