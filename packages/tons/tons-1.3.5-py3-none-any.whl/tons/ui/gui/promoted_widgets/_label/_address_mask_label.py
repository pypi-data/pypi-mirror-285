from functools import lru_cache, cached_property
from typing import Optional

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import mono_font


@lru_cache
def _address_mask_alpha() -> float:
    return 0.30


@lru_cache
def _address_mask_tail_size() -> int:
    return 5


class AddressMaskLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._address: Optional[str] = None

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, self._mask_color)
        self.setPalette(palette)
        self.setFont(mono_font())

    @cached_property
    def _mask_color(self) -> QColor:
        col = self.palette().color(QPalette.ColorRole.Text)
        col.setAlphaF(_address_mask_alpha())
        return col

    @property
    def address(self) -> Optional[str]:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value
        self.__set_address()

    def __set_address(self):
        tail = _address_mask_tail_size()
        mask = '(' + self._address[:tail] + '...' + self._address[-tail:] + ')'
        self.setText(mask)
