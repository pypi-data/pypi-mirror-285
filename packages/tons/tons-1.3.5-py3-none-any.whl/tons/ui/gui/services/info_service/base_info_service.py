import weakref
from abc import abstractmethod, ABC
from typing import Callable, Optional

from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, QTimer

from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import CtxReferenceError
from tons.ui.gui.utils import slot_exc_handler, QABCMeta


class BaseInfoService(QObject, metaclass=QABCMeta):
    UPDATE_INTERVAL_MS: int
    FORGET_INTERVAL_SEC: int

    updated = pyqtSignal()

    def __init__(self, obj_name):
        super().__init__()
        self.__ctx: Optional[weakref.ReferenceType] = None
        self._thread = QThread()
        self._thread.setObjectName(obj_name)
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run)
        self._timer = self._setup_timer()

    def setup(self, ctx: SharedObject):
        self.stop()
        self.clear()
        self.__ctx = weakref.ref(ctx)
        self.start()

    @property
    def _ctx(self) -> SharedObject:
        if (self.__ctx is None) or (self.__ctx() is None):
            raise CtxReferenceError
        return self.__ctx()

    def subscribe(self, slot: Callable):
        self.updated.connect(slot)

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.quit()
        self._thread.wait()

    def _setup_timer(self) -> QTimer:
        timer = QTimer()
        timer.setInterval(self.UPDATE_INTERVAL_MS)
        timer.timeout.connect(self._update)
        self._thread.finished.connect(timer.stop)
        timer.moveToThread(self._thread)
        return timer

    @pyqtSlot()
    @slot_exc_handler()
    def _run(self):
        self._timer.timeout.emit()
        self._timer.start()

    @abstractmethod
    def clear(self):
        raise NotImplementedError

    @pyqtSlot()
    @abstractmethod
    def _update(self):
        raise NotImplementedError
