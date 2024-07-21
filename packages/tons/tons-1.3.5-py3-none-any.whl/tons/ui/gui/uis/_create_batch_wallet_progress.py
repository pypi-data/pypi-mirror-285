from typing import Dict

from PyQt6 import QtWidgets

from ._base import ui_patch
from ._qt_assets import create_batch_wallet_progress


@ui_patch
class CreateBatchWalletProgressUI(create_batch_wallet_progress.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        matrix = dict()
        matrix[self.labelIconKeystore] = "lock-solid.svg"

        return matrix
