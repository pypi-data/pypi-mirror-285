from typing import Optional

from PyQt6.QtGui import QPalette, QColor, QFontMetrics

from ._my_line_edit import MyLineEdit


class DisabledAmountLineEdit(MyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        self.setReadOnly(True)

    def setText(self, text: Optional[str]) -> None:
        super().setText(text)
        self.__set_fixed_width_based_on_text()

    def __set_fixed_width_based_on_text(self):
        """
        Sets width of a line edit widget based on its text.

        Reference:
          https://stackoverflow.com/questions/48031291/adjusting-the-width-of-qlineedit-to-contents-and-getting-shorter-than-expected
        """
        font_metrics = QFontMetrics(self.font())
        bounding_rectangle = font_metrics.boundingRect(self.text())
        delta = self.minimumSizeHint().width()

        self.setFixedWidth(bounding_rectangle.width() + delta)
