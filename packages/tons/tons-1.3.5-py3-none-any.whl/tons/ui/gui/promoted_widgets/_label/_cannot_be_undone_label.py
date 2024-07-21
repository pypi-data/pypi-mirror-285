from functools import lru_cache

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import qt_exc_handler


@lru_cache()
def _cannot_be_undone_font() -> QFont:
    font = QFont()
    font.setPointSize(round(font.pointSize() * 11 / 13))
    font.setWeight(300)
    return font


class CannotBeUndoneLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(_cannot_be_undone_font())
        self.setDisabled(True)

    @qt_exc_handler
    def setFont(self, a0):
        super().setFont(_cannot_be_undone_font())