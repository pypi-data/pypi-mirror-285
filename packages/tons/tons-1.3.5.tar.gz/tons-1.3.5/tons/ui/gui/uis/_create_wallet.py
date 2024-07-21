from typing import Dict, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import create_wallet


@ui_patch
class CreateWalletUI(create_wallet.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        matrix = dict()
        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
