from PyQt6.QtGui import QPalette, QColor

from ._my_line_edit import MyLineEdit
from tons.ui.gui.utils import mono_font


class MultipleWallletsRangerLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(mono_font())
        self.setFixedHeight(17)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        self.setFont(mono_font())
        self.setReadOnly(True)
