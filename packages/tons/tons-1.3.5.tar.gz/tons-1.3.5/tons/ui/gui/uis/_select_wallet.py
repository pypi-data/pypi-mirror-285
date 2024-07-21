from typing import Dict, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QFrame

from tons.ui.gui.uis import ui_patch
from ._qt_assets import select_wallet


@ui_patch
class SelectWalletUI(select_wallet.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        return {
            self.pushButtonNew: 'file-circle-plus-solid.svg',
        }

    def post_setup_ui(self, form):
        self.listViewWalletsContainer.set_figma_respecting_margins()

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
