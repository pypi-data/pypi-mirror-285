from typing import Protocol, Optional

from PyQt6.QtCore import pyqtSlot, QObject

from tons.ui.gui.utils import slot_exc_handler


class Window(Protocol):
    def connect_closed(self, slot): ...


class ChildWindowManager(QObject):
    """
    A utility class to manage and control the lifecycle of child windows.

    QObjects in PyQt are destroyed when there are zero references to them.
    So in order to display a window properly, we need to hold a reference to it upon its creation.
    This class holds references to created child windows and ensures their proper destruction
    upon closing.

    For more details and discussion:
    https://stackoverflow.com/questions/65356836/how-do-i-remove-every-reference-to-a-closed-windows
    """
    def __init__(self):
        super().__init__()
        self._open_windows = []

    def add(self, window: Window):
        self._open_windows.append(window)
        window.connect_closed(self._on_window_closed)

    @pyqtSlot(object)
    @slot_exc_handler()
    def _on_window_closed(self, window: Window):
        self._open_windows.remove(window)


class SingleChildWindowManager(QObject):
    """
    Same as `ChildWindowManager`, but holds only one instance of the window at a time.

    TODO: support window reinit without closing it
    """
    def __init__(self):
        super().__init__()
        self._open_window = None

    def set(self, window: Window):
        self.close()
        self._open_window = window  # destructor
        window.connect_closed(self._on_window_closed)

    def get(self) -> Optional[Window]:
        return self._open_window

    @pyqtSlot(object)
    @slot_exc_handler()
    def _on_window_closed(self, _):
        self._open_window = None    # destructor

    def close(self):
        try:
            close_window = self._open_window.close
        except AttributeError:
            pass
        else:
            """ 
            https://stackoverflow.com/questions/1733022/qt-do-events-get-processed-in-order
            https://doc.qt.io/qt-6/eventsandfilters.html
            https://doc.qt.io/qt-6/qwidget.html#close
            """
            close_window()


__all__ = ['ChildWindowManager', 'SingleChildWindowManager']