from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import QRect, QSizeF, QSize, Qt
from PyQt6.QtGui import QPainter, QStaticText, QResizeEvent, QPixmap, QIcon, QPalette, QFont, QFontMetrics
from PyQt6.QtWidgets import QProxyStyle, QStyle, QWidget, QStyleOption

from ._my_push_button import MyPushButton
from tons.ui.gui.utils import qt_exc_handler, qt_exc_handler, fix_button_height_based_on_system, macos


class FlatIconPushButton(MyPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlat(True)


@lru_cache
def _flat_button_label_opacity() -> float:
    default_text_alpha = QPalette().color(QPalette.ColorRole.WindowText).alpha() / 0xff
    return 0.75 / default_text_alpha


class FlatIconLeftAlignedPushButtonStyle(QProxyStyle):
    icon_margin = 7
    icon_text_margin = 7
    right_margin = 7

    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], button: Optional[QWidget] = ...) -> None:
        assert isinstance(button, FlatIconLeftAlignedPushButton)
        if element != QStyle.ControlElement.CE_PushButtonLabel:
            return super().drawControl(element, option, painter, button)

        painter.save()
        painter.setOpacity(_flat_button_label_opacity())
        self._draw_icon(button, painter)
        self._draw_text(button, painter)
        painter.restore()

    def _draw_icon(self, button: 'FlatIconLeftAlignedPushButton', painter: QPainter):
        icon = button.icon()
        icon_size = button.iconSize()

        x = self.icon_margin
        y = (button.height() - icon_size.height()) // 2

        icon_rect = QRect(x, y, icon_size.width(), icon_size.height())

        mode = QIcon.Mode.Active if button.isEnabled() else QIcon.Mode.Disabled
        icon.paint(painter, icon_rect, mode=mode)

    def _draw_text(self, button: 'FlatIconLeftAlignedPushButton', painter: QPainter):
        static_text = button.static_text()
        x = int(self.icon_margin + button.iconSize().width() + self.icon_text_margin)
        y = int((button.height() - static_text.size().height()) // 2)
        painter.drawStaticText(x, y, static_text)


class FlatIconLeftAlignedPushButton(FlatIconPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(FlatIconLeftAlignedPushButtonStyle())

    def _set_size(self):
        fix_button_height_based_on_system(self)
        self._set_fixed_width()
        self.parent().update()  # for an instant display, removes lag animation during window init

    @qt_exc_handler
    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self._set_size()

    def _set_fixed_width(self):
        text_size = self.static_text_size()
        st = FlatIconLeftAlignedPushButtonStyle
        frame_width = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
        width = int(st.icon_margin + self.iconSize().width() +
                    st.icon_text_margin + text_size.width() +
                    st.right_margin + frame_width * 2)
        self.setFixedWidth(width)

    @lru_cache(maxsize=None)
    def static_text(self):
        return QStaticText(self.text())

    @lru_cache(maxsize=None)
    def static_text_size(self) -> QSizeF:
        return self.static_text().size()


class FlatIconLeftAlignedPushButtonWithArrowStyle(FlatIconLeftAlignedPushButtonStyle):
    arrow_side = 8
    arrow_margin = 7

    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], button: Optional[QWidget] = ...) -> None:
        assert isinstance(button, FlatIconLeftAlignedPushButtonWithArrow)
        if element != QStyle.ControlElement.CE_PushButtonLabel:
            return super().drawControl(element, option, painter, button)

        painter.save()
        painter.setOpacity(_flat_button_label_opacity())
        self._draw_icon(button, painter)
        self._draw_text(button, painter)
        self._draw_arrow(button, painter)
        painter.restore()

    def _draw_arrow(self, button: 'FlatIconLeftAlignedPushButtonWithArrow', painter: QPainter):
        if not button.isEnabled():
            return

        static_text = button.static_text()

        x = int(self.icon_margin + button.iconSize().width() + self.icon_text_margin)
        x += int(static_text.size().width() + self.arrow_margin)
        y = int(round((button.height() - self.arrow_side) / 2))
        arrow_option = QStyleOption()
        arrow_option.rect = QRect(x, y, self.arrow_side, self.arrow_side)

        super().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorArrowDown, arrow_option, painter, button)

    @qt_exc_handler
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: Optional['QStyleOption'],
                      painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.PrimitiveElement.PE_IndicatorArrowDown:
            return
        super().drawPrimitive(element, option, painter, widget)


class FlatIconLeftAlignedPushButtonWithArrow(FlatIconLeftAlignedPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(FlatIconLeftAlignedPushButtonWithArrowStyle())

    def _set_fixed_width(self):
        super()._set_fixed_width()
        st = FlatIconLeftAlignedPushButtonWithArrowStyle
        self.setFixedWidth(self.width() + st.arrow_side + st.arrow_margin)


@lru_cache()
def _font_smaller():
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    font.setWeight(300)
    return font

@lru_cache
def _fixed_height() -> int:
    return 32


@lru_cache
def _rect_height() -> int:
    return 19


class FlatIconLeftAlignedPushButtonSmallerFontStyle(FlatIconLeftAlignedPushButtonStyle):
    icon_margin = 7
    icon_text_margin = 7
    right_margin = 7

    def _draw_text(self, button: 'FlatIconLeftAlignedPushButton', painter: QPainter):
        static_text = button.static_text()
        x = int(self.icon_margin + button.iconSize().width() + self.icon_text_margin)
        y = int((button.height() - static_text.size().height()) // 2)
        painter.drawStaticText(x, y, static_text)

    def _draw_icon(self, button: 'FlatIconLeftAlignedPushButton', painter: QPainter):
        icon = button.icon()
        icon_size = button.iconSize()

        x = self.icon_margin
        y = (button.height() - icon_size.height()) // 2

        icon_rect = QRect(x, y, icon_size.width(), icon_size.height())

        mode = QIcon.Mode.Active if button.isEnabled() else QIcon.Mode.Disabled
        icon.paint(painter, icon_rect, mode=mode)

class FlatIconLeftAlignedPushButtonSmallerFont(FlatIconLeftAlignedPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(_font_smaller())
        self.setStyle(FlatIconLeftAlignedPushButtonSmallerFontStyle())

    @qt_exc_handler
    def setText(self, text: Optional[str]) -> None:
        text = text or ''
        super().setText(text)
        self.__set_size()

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
        text_size = self.static_text_size()
        s = FlatIconLeftAlignedPushButtonSmallerFontStyle
        width = (text_size.width() + 16 + s.icon_text_margin + s.right_margin + s.icon_margin)
        self.setFixedWidth(width)

    def static_text_size(self) -> QSize:
        font_metrics = QFontMetrics(self.font())
        rect = font_metrics.boundingRect(self.text())
        size = QSize(rect.width(), rect.height())
        return size
