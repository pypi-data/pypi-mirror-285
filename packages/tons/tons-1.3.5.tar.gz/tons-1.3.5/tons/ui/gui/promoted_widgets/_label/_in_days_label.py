from functools import lru_cache
from typing import Optional

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QLabel


@lru_cache
def _in_days_alpha() -> float:
    return 0.30


class InDaysLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._days: Optional[int] = None
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, self._mask_color)
        self.setPalette(palette)

    @property
    def _mask_color(self) -> QColor:
        col = self.palette().color(QPalette.ColorRole.Text)
        col.setAlphaF(_in_days_alpha())
        return col

    # @property
    # def days(self) -> Optional[int]:
    #     return self._days
    #
    # @days.setter
    # def days(self, value: int):
    #     self._days = int(value)
    #     self.__set_days()
    #
    # def __set_days(self):
    #     self.setText(f'(in {self._days} days)')

