from functools import lru_cache

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QWidget

from tons.ui.gui.utils import macos


@lru_cache
def _alpha() -> float:
    return .9


class SideBarWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        if macos():
            palette = self.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            window_color = QColor(int(window_color.red() * _alpha()),
                                  int(window_color.green() * _alpha()),
                                  int(window_color.blue() * _alpha())
                                  )
            palette.setColor(QPalette.ColorRole.Window, window_color)
            self.setPalette(palette)


__all__ = ['SideBarWidget']