from functools import cached_property
from typing import Optional, Union, Tuple

from PyQt6.QtCore import QRect, QPointF, QPropertyAnimation, QAbstractAnimation, QRectF, Qt
from PyQt6.QtGui import QResizeEvent, QPaintEvent, QColor, QPainter, QStaticText, QPixmap
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from pydantic import BaseModel

from tons.ui.gui.utils import theme_is_dark, invert_color, elide_rich_text, RichTextElideMode, blend_alpha, \
    qt_exc_handler, get_icon_pixmap


class NotificationBarMessage(BaseModel):
    text: str
    good: Optional[bool] = None


class NotificationBar(QWidget):
    height = 48
    margin_vertical = 9
    margin_horizontal = 8

    horizontal_padding = 16

    border_radius = 5

    icon_width = 16
    icon_spacing = 7

    @cached_property
    def color(self):
        if theme_is_dark():
            return blend_alpha(QColor(0x1C, 0x1D, 0x1F), QColor(0, 0, 0), 0.15)
        if not theme_is_dark():
            return QColor(0xCF, 0xD1, 0xCF)

    @cached_property
    def text_color(self):
        col = QColor(223, 223, 223, int(0.75 * 0xff))
        if not theme_is_dark():
            return invert_color(col)
        return col

    @cached_property
    def error_text_color(self) -> QColor:
        # ED6A5F
        return QColor(0xED, 0x6A, 0x5F)

    @cached_property
    def success_icon_pixmap(self) -> QPixmap:
        return get_icon_pixmap('round_check.svg')

    @cached_property
    def error_icon_pixmap(self) -> QPixmap:
        return get_icon_pixmap('exclamation.svg')

    def __init__(self, container: QWidget, *args,  **kwargs):
        self._container = container
        self._message: Optional[NotificationBarMessage] = None
        super().__init__(*args, **kwargs)
        self._container.installEventFilter(self)
        self.setParent(self._container.parent())

        self._opacity_effect = self._setup_opacity_effect()
        self._animation = self._setup_animation()

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setup_opacity_effect(self):
        eff = QGraphicsOpacityEffect()
        eff.setOpacity(0)
        self.setGraphicsEffect(eff)
        return eff

    def _setup_animation(self) -> QAbstractAnimation:
        a = QPropertyAnimation()
        a.setTargetObject(self._opacity_effect)
        a.setPropertyName(b'opacity')
        a.setDuration(500)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        return a

    def _smooth_appear(self):
        self._animation.setDirection(QPropertyAnimation.Direction.Forward)
        if self._animation.currentTime() != self._animation.duration():
            self._animation.start()

    def _smooth_disappear(self):
        self._animation.setDirection(QPropertyAnimation.Direction.Backward)
        if self._animation.currentTime() != 0:
            self._animation.start()

    def show_message(self, message: Union[None, NotificationBarMessage, str]):
        if isinstance(message, str):
            self._message = NotificationBarMessage(text=message)
        else:
            self._message = message
        self.repaint()
        self._smooth_appear()

    def hide_(self):
        self._smooth_disappear()

    @qt_exc_handler
    def eventFilter(self, obj: Optional['QObject'], event: Optional['QEvent']) -> bool:
        if obj == self._container and isinstance(event, QResizeEvent):
            self._adjust_geometry_to_container(
                QRect(
                    self._container.pos(),
                    event.size()
                )
            )
        return False

    def _adjust_geometry_to_container(self, container_geometry: Optional[QRect] = None):
        container_geometry = container_geometry or self._container.geometry()
        my_geo = QRect(
                container_geometry.left() + self.margin_horizontal,
                container_geometry.bottom() - self.height - self.margin_vertical,
                container_geometry.width() - self.margin_horizontal * 2,
                self.height
            )
        self.setGeometry(
            my_geo
        )
        self.repaint()

    @qt_exc_handler
    def paintEvent(self, a0: Optional[QPaintEvent]):
        if self._message is None:
            return
        self._paint_rectangle()
        self._paint_message()

    def _paint_rectangle(self):
        painter = QPainter(self)
        painter.setPen(self.color)
        painter.setBrush(self.color)
        painter.drawRoundedRect(self.geometry().translated(-self.x(), -self.y()),
                                self.border_radius,
                                self.border_radius)

    def _icon_pixmap(self) -> Optional[QPixmap]:
        try:
            if self._message.good is None:
                return None
        except AttributeError:
            return None

        if self._message.good:
            return self.success_icon_pixmap

        return self.error_icon_pixmap

    def _static_text(self) -> QStaticText:
        text = elide_rich_text(self._message.text, self._max_text_width(), elide_mode=RichTextElideMode.right)
        return QStaticText(text)

    def _max_text_width(self) -> int:
        return self.geometry().width() - self.horizontal_padding*2 - self.icon_width - self.icon_spacing

    def _paint_message(self):
        painter = QPainter(self)
        static_text = self._static_text()
        pixmap = self._icon_pixmap()

        text_x = (self.geometry().width() - static_text.size().width()) / 2
        text_y = (self.geometry().height() - static_text.size().height()) / 2
        if pixmap is not None:
            text_x += (self.icon_width + self.icon_spacing) / 2

        painter.setPen(self.text_color)
        if self._message.good is False:
            painter.setPen(self.error_text_color)
        painter.drawStaticText(QPointF(text_x, text_y), static_text)

        if pixmap is not None:
            icon_height = pixmap.size().height() * self.icon_width / pixmap.size().width()
            icon_rect = QRectF(text_x - self.icon_width - self.icon_spacing,
                               self.geometry().height() / 2 - icon_height / 2,
                               self.icon_width,
                               icon_height)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.drawPixmap(icon_rect.toRect(), pixmap)


__all__ = ['NotificationBar', 'NotificationBarMessage']
