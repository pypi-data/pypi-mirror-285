from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QStackedWidget


class MyStackedWidget(QStackedWidget):
    """ Automatically adjusts it size to the current widget
    TODO: make this class work for a resizeable window
    """
    def minimumSizeHint(self) -> QSize:
        return self.currentWidget().minimumSize()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.currentChanged.connect(self.__on_current_changed)

    # def __on_current_changed(self, index: int):
    #     pass
