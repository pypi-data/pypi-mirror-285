from typing import Optional, Union

from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QListView

from tons.ui.gui.utils import qt_exc_handler


class VerticalScrollBarEventFilter(QObject):
    """ Crutch to adjust size when the vertical scroll bar is showed"""

    # TODO remove?
    def __init__(self, widget: QListWidget):
        super().__init__()
        self._list_widget = widget
        self._scroll_bar = widget.verticalScrollBar()
        self._scroll_bar.installEventFilter(self)

    @qt_exc_handler
    def eventFilter(self, object_: Optional[QObject], event: Optional[QEvent]) -> bool:
        if object_ == self._scroll_bar:
            if event.type() == QEvent.Type.Show:
                list_widget_item = QListWidgetItem('dummy')
                self._list_widget.addItem(list_widget_item)
                idx = self._list_widget.indexFromItem(list_widget_item)
                self._list_widget.takeItem(idx.row())
        return False


class ForbidKeyMovementEventFilter(QObject):
    """ Forbid vertical movement with arrow keys in list widgets """
    def __init__(self, list_widget: Union[QListWidget, QListView]):
        super().__init__()
        self._list_widget = list_widget
        self._list_widget.installEventFilter(self)

    @qt_exc_handler
    def eventFilter(self, object_: Optional[QObject], event: Optional[QEvent]) -> bool:
        if object_ == self._list_widget:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() in [Qt.Key.Key_Down, Qt.Key.Key_Up]:
                    return True
        return False


class UpdateOnMouseMovementFilter(QObject):
    def __init__(self, widget: QWidget):
        super().__init__()
        self._widget = widget
        self._widget.installEventFilter(self)

    @qt_exc_handler
    def eventFilter(self, object_: Optional[QObject], event: Optional[QEvent]) -> bool:
        if event.type() == QEvent.Type.MouseMove:
            self._widget.update()

        return False
