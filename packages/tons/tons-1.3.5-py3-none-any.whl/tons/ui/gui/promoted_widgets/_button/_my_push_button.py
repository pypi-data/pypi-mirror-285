from typing import Optional

from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QPushButton

from tons.ui.gui.utils import qt_exc_handler, fix_button_height_based_on_system


class MyPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @qt_exc_handler
    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        fix_button_height_based_on_system(self)
