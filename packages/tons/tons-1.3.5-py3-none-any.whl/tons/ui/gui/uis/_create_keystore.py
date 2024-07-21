from typing import Sequence

from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import create_keystore


@ui_patch
class CreateKeystoreUI(create_keystore.Ui_Form):
    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
