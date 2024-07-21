from functools import lru_cache

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter, QColor

from ._base import AbstractLoader


@lru_cache(maxsize=2048)
def _dash_loader_rectangles(width: int, height: int, frame_id: int, max_frame_id: int, relative_height: float,
                            rice_relative_width: float, relative_vertical_shift: float):
    dash_width = width
    dash_height = height * relative_height
    dash_x = 0
    dash_y = height / 2 - dash_height / 2 + relative_vertical_shift * height
    rice_width = width * rice_relative_width
    rice_height = dash_height
    rice_x = ((width + rice_width) / max_frame_id) * frame_id - rice_width
    rice_y = dash_y
    rice_rectangle = QRect(int(rice_x), int(rice_y), int(rice_width), int(rice_height))
    dash_rectangle = QRect(int(dash_x), int(dash_y), int(dash_width), int(dash_height))
    return dash_rectangle, rice_rectangle


class DashLoader(AbstractLoader):
    def __init__(self, rice_color: QColor, dash_color: QColor, rice_relative_width: float, relative_height: float,
                 relative_vertical_shift: float, draw_dash: bool = True):
        self._rice_color = rice_color
        self._dash_color = dash_color
        self._rice_relative_width = rice_relative_width
        self._relative_height = relative_height
        self._relative_vertical_shift = relative_vertical_shift
        self._draw_dash = draw_dash

    def _paint_in_rect(self, painter: QPainter, width: int, height: int, frame_id: int, max_frame_id: int):
        relative_height = self._relative_height
        rice_relative_width = self._rice_relative_width
        relative_vertical_shift = self._relative_vertical_shift

        dash_rectangle, rice_rectangle = _dash_loader_rectangles(width, height, frame_id, max_frame_id, relative_height,
                                                                 rice_relative_width, relative_vertical_shift)

        painter.setPen(Qt.PenStyle.NoPen)
        if self._draw_dash:
            painter.setBrush(self._dash_color)
            painter.drawRect(dash_rectangle)
        painter.setBrush(self._rice_color)
        painter.drawRect(rice_rectangle)
