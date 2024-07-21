from typing import Optional

from PyQt6.QtGui import QPalette, QColor, QFontMetrics
from PyQt6.QtWidgets import QLineEdit

from ._my_line_edit import MyLineEdit
from tons.ui.gui.utils import mono_font, macos


class AddressLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0,0,0,0))
        self.setPalette(palette)
        self.setFont(mono_font())
        self.setReadOnly(True)

    def setText(self, text: Optional[str]) -> None:
        super().setText(text)
        self.__set_fixed_width_based_on_text()

    def __set_fixed_width_based_on_text(self):
        _set_fixed_width_based_on_text(self)

class AddressLineEditableEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(mono_font())

    def setText(self, a0):
        """ Set size enough to fit a user-friendly address """
        super().setText(a0)
        address_mock = 'U' * 48
        _set_fixed_width_based_on_text(self, address_mock)


def _set_fixed_width_based_on_text(line_edit: QLineEdit, text: Optional[str] = None):
    """
    Sets width of a line edit widget based on its text.

    Reference:
      https://stackoverflow.com/questions/48031291/adjusting-the-width-of-qlineedit-to-contents-and-getting-shorter-than-expected
    """
    font_metrics = QFontMetrics(line_edit.font())
    text = text or line_edit.text()
    bounding_rectangle = font_metrics.boundingRect(text)
    delta = line_edit.minimumSizeHint().width()
    if macos():
        delta += 3

    line_edit.setFixedWidth(bounding_rectangle.width() + delta)