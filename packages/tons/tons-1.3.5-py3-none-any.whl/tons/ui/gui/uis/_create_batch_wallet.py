from typing import Sequence

from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import create_batch_wallet


@ui_patch
class CreateBatchWalletUI(create_batch_wallet.Ui_Form):
    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
