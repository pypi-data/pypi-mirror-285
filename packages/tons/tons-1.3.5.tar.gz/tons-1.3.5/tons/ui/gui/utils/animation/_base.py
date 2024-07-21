from abc import ABCMeta, abstractmethod

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPainter


class AbstractAnimation(metaclass=ABCMeta):
    def paint(self, painter: QPainter, rect: QRect, frame_id: int, max_frame_id: int):
        painter.save()
        painter.setClipRect(rect)
        painter.translate(rect.topLeft())
        self._paint_in_rect(painter, rect.width(), rect.height(), frame_id, max_frame_id)
        painter.restore()

    @abstractmethod
    def _paint_in_rect(self, painter: QPainter, width: int, height: int, frame_id: int, max_frame_id: int):
        raise NotImplementedError
