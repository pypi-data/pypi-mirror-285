from typing import Optional

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPainter, QPalette
from PyQt6.QtWidgets import QLabel, QProxyStyle

from tons.ui.gui.utils import extract_ellipse_symbol, remove_circle_symbols, draw_state_ellipse, qt_exc_handler


class WalletStateLabelStyle(QProxyStyle):
    circle_diameter = 6
    circle_gap = 4

    @qt_exc_handler
    def drawItemText(self, painter: Optional[QPainter], rect: QRect, flags: int, pal: QPalette, enabled: bool,
                     text: Optional[str], textRole: QPalette.ColorRole = ...) -> None:
        symbol = extract_ellipse_symbol(text)

        if symbol is None:
            return super().drawItemText(painter, rect, flags, pal, enabled, text, textRole)

        draw_state_ellipse(symbol, rect, painter, self.circle_diameter / 2)

        dx = self.circle_diameter + self.circle_gap

        super().drawItemText(painter,
                             rect.translated(dx, 0), flags, pal, enabled,
                             remove_circle_symbols(text), textRole)


class WalletStateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(WalletStateLabelStyle())
