from typing import Dict, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFrame

from tons.ui.gui.uis import ui_patch
from ._qt_assets import transactions_history


@ui_patch
class TransactionsHistoryUI(transactions_history.Ui_Form):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        return {
            self.pushButtonCancelAll: 'square-xmark-solid.svg'
        }

    def post_setup_ui(self, form):
        self.listViewTransactionsContainer.set_figma_respecting_margins()

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
