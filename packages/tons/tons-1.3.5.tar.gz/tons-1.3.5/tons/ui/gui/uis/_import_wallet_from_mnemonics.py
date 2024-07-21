from typing import Dict, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import import_wallet_from_mnemonics


@ui_patch
class ImportWalletFromMnemonicsUI(import_wallet_from_mnemonics.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        matrix = dict()
        matrix[self.labelTonIcon] = "ton_symbol.svg"
        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
