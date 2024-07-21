from functools import lru_cache
from typing import Optional, Any

from PyQt6.QtCore import QRect, QPointF, QSize
from PyQt6.QtGui import QPainter, QStaticText, QFont
from PyQt6.QtWidgets import QComboBox, QProxyStyle, QStyle, QWidget, QStyleOptionComplex, QStyleOptionComboBox, \
    QStyleOption

from tons.ui.gui.utils import qt_exc_handler, windows


@lru_cache(maxsize=None)
def sort_by_font() -> QFont:
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    return font


@lru_cache(maxsize=256)
def _get_styled_static_text(text: str) -> QStaticText:
    static_text = QStaticText(text)
    static_text.prepare(font=sort_by_font())
    return static_text


@lru_cache(maxsize=256)
def _get_text_pos(rect_height: int, static_text_height: float) -> QPointF:
    text_pos = QPointF(
        0,
        (rect_height - static_text_height) / 2
    )
    return text_pos


@lru_cache(maxsize=None)
def _arrow_size() -> QSize:
    return QSize(8,8)


@lru_cache(maxsize=256)
def _get_arrow_rect(text_pos_x: float, static_text_width: float, spacing: int, rect_top: int, rect_height: int) -> QRect:
    aw = _arrow_size().width()
    ah = _arrow_size().height()
    ax = int(text_pos_x + static_text_width + spacing)
    ay = int(rect_top + (rect_height - ah) / 2)
    return QRect(ax, ay, aw, ah)


@lru_cache(maxsize=256)
def _get_widget_width(text: str, spacing: int) -> int:
    width = int(_get_styled_static_text(text).size().width())
    width += spacing
    width += _arrow_size().width()
    assert isinstance(width, int)
    return width


class SortByComboStyle(QProxyStyle):
    box_height = 13
    spacing = 7

    @qt_exc_handler
    def drawComplexControl(self, control: QStyle.ComplexControl,
                           option: Optional['QStyleOptionComplex'], painter: Optional[QPainter],
                           widget: Optional[QWidget] = ...) -> None:
        return

    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if element == QStyle.ControlElement.CE_ComboBoxLabel and isinstance(option, QStyleOptionComboBox):

            static_text = _get_styled_static_text(option.currentText)
            text_pos = _get_text_pos(option.rect.height(), static_text.size().height())

            painter.drawStaticText(text_pos, static_text)

            arrow_option = QStyleOption()
            arrow_option.rect = _get_arrow_rect(text_pos.x(), static_text.size().width(), self.spacing,
                                                option.rect.top(), option.rect.height())

            super().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorArrowDown, arrow_option, painter, None)

            return

        return super().drawControl(element, option, painter, widget)


class SortByComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(SortByComboStyle())
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        super().setFont(sort_by_font())
        self.currentTextChanged.connect(self._on_current_text_changed)

        self.__view_width: Optional[int] = None

    def _on_current_text_changed(self, text: str):
        self._set_fixed_width(text)

    def _set_fixed_width(self, text: str):
        width = _get_widget_width(text, SortByComboStyle.spacing)
        self.setFixedWidth(width)

    @qt_exc_handler
    def addItem(self, text: Optional[str], userData: Any = None) -> None:
        super().addItem(text, userData)
        if windows():  # (?)
            self._adjust_view_width(text)

    def _adjust_view_width(self, text: str):
        text_width = _get_widget_width(text, SortByComboStyle.spacing)
        if self._view_width is None or text_width > self._view_width:
            self._view_width = text_width

    @property
    def _view_width(self) -> Optional[int]:
        return self.__view_width

    @_view_width.setter
    def _view_width(self, value: int):
        self.__view_width = value
        self.view().setFixedWidth(self.__view_width)

