from typing import Tuple, Dict, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import create_contact


@ui_patch
class CreateContactUI(create_contact.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        matrix = dict()
        matrix[self.labelTonIcon] = "ton_symbol.svg"
        matrix[self.pushButtonShowInScanner] = "users-viewfinder-solid.svg"
        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
