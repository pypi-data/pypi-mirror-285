from functools import lru_cache
from typing import Dict, Tuple, Optional

from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter

from tons.ui.gui.utils import theme_is_dark, invert_color, RichString

""" 
Monkey-patchy approach to preserve compatibility with v1 (non pixel perfect) UI
TODO Might be a good idea to refactor 
"""


@lru_cache(maxsize=None)
def ellipse_pen_and_brush_map() -> Dict[str, Tuple[QPen, QBrush]]:
    matrix = dict()

    non_exist_border_color = QColor(223, 222, 223)
    if not theme_is_dark():
        non_exist_border_color = invert_color(non_exist_border_color)
    non_exist_border_color.setAlpha(0x80)

    uninit_border_color = Qt.PenStyle.NoPen if theme_is_dark() else non_exist_border_color

    matrix['⚪'] = QPen(uninit_border_color), QBrush(QColor(0xFF, 0xFF, 0xFF, 0x80))
    matrix['🔵'] = QPen(Qt.PenStyle.NoPen), QBrush(QColor(0x7A, 0xD7, 0xF0, 0x80))
    matrix['🟢'] = QPen(Qt.PenStyle.NoPen), QBrush(QColor(0x61, 0xC5, 0x54, 0x80))  # figma
    matrix['◯'] = QPen(non_exist_border_color), QBrush(QColor(0, 0, 0, 0))

    return matrix


@lru_cache(maxsize=32)
def extract_ellipse_symbol(text: str) -> Optional[str]:
    for symbol in ellipse_pen_and_brush_map():
        if symbol in text:
            return symbol


@lru_cache(maxsize=32)
def remove_circle_symbols(text: str) -> str:
    for symbol in ellipse_pen_and_brush_map():
        text = text.replace(symbol, '')

    if RichString(text).clean_string.endswith(' '):
        text = RichString(text)[:-1]

    return text.strip()


def draw_state_ellipse(symbol: str, rect: QRect, painter: QPainter, radius: float):
    ellipse_center = QPointF(rect.x() + radius,
                             rect.y() + rect.height() / 2)

    pen, brush = ellipse_pen_and_brush_map()[symbol]
    painter.save()
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawEllipse(ellipse_center, radius, radius)
    painter.restore()
