from PyQt6.QtWidgets import QProxyStyle, QStyle, QPushButton

from tons.ui.gui.utils import qt_exc_handler


class LineEditButtonStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element, option, painter, widget = ...):
        if element == QStyle.ControlElement.CE_PushButtonBevel:
            return
        return super().drawControl(element, option, painter, widget)


class LineEditButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(LineEditButtonStyle())
