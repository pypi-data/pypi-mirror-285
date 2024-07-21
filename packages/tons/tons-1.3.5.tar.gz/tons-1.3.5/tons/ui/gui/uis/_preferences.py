from typing import Tuple, Sequence

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFrame

from ._base import ui_patch
from ._qt_assets import preferences


@ui_patch
class PreferencesUI(preferences.Ui_Form):
    def post_setup_ui(self, form):
        button_box: QtWidgets.QDialogButtonBox = self.buttonBox
        save_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        save_button.setDisabled(True)
        self.labelPathValidationError.setVisible(False)

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line1, self.line2, self.line3, self.line4
