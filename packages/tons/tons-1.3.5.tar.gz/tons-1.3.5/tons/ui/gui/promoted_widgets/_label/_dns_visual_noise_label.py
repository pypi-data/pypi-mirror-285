from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import macos, windows


class DnsVisualNoiseLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, self._visual_noise_color)
        self.setPalette(palette)
        font = self.font()
        font.setPointSize(self._font_size)
        self.setFont(font)

    @property
    def _visual_noise_color(self) -> QColor:
        col = self.palette().color(QPalette.ColorRole.Text)
        col.setAlphaF(0.4)
        return col

    @property
    def _font_size(self) -> int:
        if macos():
            return 11
        if windows():
            return 8
        return round(self.font().pointSizeF() * 11 / 13)
