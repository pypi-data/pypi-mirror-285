import uuid
import weakref
from typing import Iterator, Tuple, Protocol

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from tons.config import TonScannerEnum
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.services import tx_info_service
from tons.ui.gui.utils import BackgroundTaskService, slot_exc_handler, BroadcastTask, BroadcastTaskResult


class BackgroundTaskServiceNotAvailableError(GuiException):
    pass


class Presenter(Protocol):
    def on_transactions_queue_changed(self): ...
    def on_tx_info_fetched(self, tx_hash: str): ...


class TransactionsHistoryModel(QObject):
    _sig_transactions_changed = pyqtSignal()

    def __init__(self, ctx: SharedObject, background_task_service: BackgroundTaskService):
        super().__init__()
        self.__ctx = weakref.ref(ctx)
        background_task_service.connect_transactions_changed(self._on_transactions_changed)
        self.__background_service = weakref.ref(background_task_service)

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def setup_signals(self, presenter: Presenter):
        self._sig_transactions_changed.connect(presenter.on_transactions_queue_changed)
        tx_info_service().fetched.connect(presenter.on_tx_info_fetched)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_transactions_changed(self):
        self._sig_transactions_changed.emit()

    def _background_service(self) -> BackgroundTaskService:
        if self.__background_service() is None:
            raise BackgroundTaskServiceNotAvailableError
        return self.__background_service()

    def task_is_taken(self, task_id: uuid.UUID) -> bool:
        return self._background_service().task_is_taken(task_id)

    def task_is_cancelled(self, task_id: uuid.UUID) -> bool:
        return self._background_service().task_is_cancelled(task_id)

    def network_is_testnet(self) -> bool:
        return self._background_service().network_is_tesnet()

    def pending_tasks(self) -> Iterator[Tuple[uuid.UUID, BroadcastTask]]:
        yield from self._background_service().pending_tasks

    def finished_tasks(self) -> Iterator[Tuple[uuid.UUID, BroadcastTaskResult]]:
        yield from self._background_service().finished_tasks

    def scanner(self) -> TonScannerEnum:
        return self._ctx.config.gui.scanner
