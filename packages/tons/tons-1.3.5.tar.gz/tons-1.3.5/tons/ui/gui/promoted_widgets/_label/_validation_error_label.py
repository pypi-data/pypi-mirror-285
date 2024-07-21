from typing import Optional

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import validation_error_color, macos


class ValidationErrorLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, validation_error_color())
        self.setPalette(palette)
        self.hide()

    def setText(self, text: Optional[str]):
        if text is None:
            super().setText(text)
        symb = '􀇿' if macos() else '⚠'
        super().setText(symb + ' ' + text)
