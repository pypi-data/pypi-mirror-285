from typing import Optional

from PyQt6.QtGui import QPalette, QColor, QMouseEvent
from PyQt6.QtWidgets import QListView, QFrame
from tons.ui.gui.utils import set_selection_color_for_light_theme, theme_is_dark, qt_exc_handler

_FIGMA_RESPECTING_MARGINS: bool = True


class WalletsListContainer(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if theme_is_dark():
            pal = self.palette()
            pal.setColor(QPalette.ColorRole.Base, QColor(0x1C,0x1D,0x1F))
            self.setPalette(pal)

        if _FIGMA_RESPECTING_MARGINS:
            self.set_figma_respecting_margins()

    def set_figma_respecting_margins(self):
        pal = self.palette()
        base_color = pal.color(QPalette.ColorRole.Base)
        pal.setColor(QPalette.ColorRole.Window, base_color)
        self.setPalette(pal)
        self.setAutoFillBackground(True)


class WalletsListView(QListView):
    # TODO rename this class (it's for wallets and dns)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_selection_color_for_light_theme(self)
        self.setFrameShape(QFrame.Shape.NoFrame)

    def setStyleSheet(self, _) -> None:
        assert False

    @qt_exc_handler
    def mouseMoveEvent(self, e: Optional[QMouseEvent]) -> None:
        self.viewport().update()
