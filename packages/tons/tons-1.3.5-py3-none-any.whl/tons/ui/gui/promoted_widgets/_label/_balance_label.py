from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import mono_font


class BalanceLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(mono_font())
        self.setFixedHeight(17)
