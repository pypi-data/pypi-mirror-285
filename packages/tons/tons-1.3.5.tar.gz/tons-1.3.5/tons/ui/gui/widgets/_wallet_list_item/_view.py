from typing import Optional

from PyQt6.QtGui import QPaintEvent, QPainter
from PyQt6.QtWidgets import QWidget

from ._delegate import draw_model_in_rectangle
from ._item_data import WalletListItemData
from .._base import AbstractListItemView
from ...utils import qt_exc_handler


class WalletListItemView(AbstractListItemView):
    def __init__(self, *, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._model: Optional[WalletListItemData] = None

    def display_model(self, model: WalletListItemData):
        self._model = model

    @qt_exc_handler
    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        if self._model is None:
            return
        painter = QPainter(self)
        draw_model_in_rectangle(painter, self.geometry(), self._model)


__all__ = ['WalletListItemView']
