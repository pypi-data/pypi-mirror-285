import contextlib
import os
import queue
import uuid
import weakref
from decimal import Decimal
from functools import lru_cache
from typing import Union, List, Dict, Callable, Any, Optional, Sequence, Set, Iterator, Tuple

from PyQt6.QtCore import QObject, QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtTest import QSignalSpy
from pydantic import BaseModel, root_validator

from tons.config import TonNetworkEnum
from tons.logging_ import tons_logger
from tons.tonclient import TonError
from tons.tonclient._client._base import TonDaemon, DaemonTask, \
    TonDaemonResult, TonDaemonGoodbye, TonDaemonDeathNote, \
    TonDaemonResponse, BroadcastResult, BroadcastStatusEnum, AddressInfoResult, NftItemInfoResult, TonDaemonTaskTaken
from tons.tonclient.utils import KeyStoreTypeEnum, BaseKeyStore
from tons.tonsdk.contract.wallet import Wallets
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject
from tons.ui.gui.services import address_info_service, AddressInfoNotFetched
from tons.ui.gui.utils import slot_exc_handler
from tons.utils import storage
from tons.utils.exceptions import StorageError
from ._actions import ActionsHistory, TransferTask, BroadcastTaskResult, DnsRefreshTask, \
    DeployWalletTask, ExportWalletTask, BroadcastTask
from ._notifications import SystemNotification
from ..exceptions import CtxReferenceError


class ErrorNotification(BaseModel):
    exception: Optional[Exception]
    title: str = 'Unexpected error'
    message: Optional[str]
    critical: bool = False

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=False)
    def __validate(cls, values):
        if values.get('message', None) is None:
            values['message'] = str(values['exception']) or repr(values['exception'])
        return values


class BackgroundTaskService(QObject):
    """ Runs in the background, receives tasks, performs them and shows notifications. """

    _error = pyqtSignal(ErrorNotification)
    _system_notify = pyqtSignal(SystemNotification)
    _queue_changed = pyqtSignal()

    def __init__(self, ctx: SharedObject, actions_history: ActionsHistory):
        super().__init__()
        self.__ctx = weakref.ref(ctx)
        self._thread = QThread()
        self.moveToThread(self._thread)

        self.daemon_observer = BroadcastDaemonObserver(self._ctx.ton_daemon)
        self.daemon_observer.got_response.connect(self.on_response_from_daemon)
        self.daemon_observer.start()

        self._actions_history = actions_history
        self._busy = False

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def connect_error(self, slot: Callable[[ErrorNotification], Any]):
        self._error.connect(slot)

    def connect_system_notify(self, slot: Callable[[SystemNotification], Any]):
        self._system_notify.connect(slot)

    def connect_transactions_changed(self, slot):
        self._queue_changed.connect(slot)

    @property
    def busy(self) -> bool:
        return self._busy or self._actions_history.any_pending

    def start(self):
        self._thread.start()

    def stop(self):
        self.daemon_observer.stop()
        self._thread.quit()
        self._thread.wait()

    def halt(self):
        """ to be called on program exit """
        self.daemon_observer.stop()
        self._thread.quit()
        self._thread.wait(3000)

    def __del__(self):
        try:
            running = self._thread.isRunning()
        except RuntimeError:  # (C++ object has been deleted)
            running = False
        log = tons_logger().error if running else tons_logger().debug
        log(f'background task service deleted ({running=})')

    @property
    def pending_tasks(self) -> Iterator[Tuple[uuid.UUID, BroadcastTask]]:
        yield from self._actions_history.pending_tasks

    @property
    def finished_tasks(self) -> Iterator[Tuple[uuid.UUID, BroadcastTaskResult]]:
        yield from self._actions_history.broadcast_results

    @contextlib.contextmanager
    def busy_context(self):
        self._busy = True
        try:
            yield
        except Exception:
            raise
        finally:
            self._busy = False

    @pyqtSlot(TransferTask)
    @slot_exc_handler()
    def on_transfer_task(self, task: TransferTask):
        self._show_notification(f'Transfer to {task.recipient.name}', "Sending transaction")

        with self.busy_context():
            wallet = task.wallet
            messages = [task.transfer_message]
            task_id = self._ctx.ton_daemon.transfer(wallet, messages)
            self._actions_history.add_pending_task(task_id, task)

        self._queue_changed.emit()

    @pyqtSlot(list)
    @slot_exc_handler()
    def on_dns_tasks(self, tasks: List[DnsRefreshTask]):
        self._show_notification(f'Refresh {self._dns_domains_count(tasks)} DNS domains',
                                "Sending transaction")

        for task in tasks:
            with self.busy_context():
                wallet = task.wallet
                task_id = self._ctx.ton_daemon.refresh_dns_ownership(wallet, task.dns_items)
                self._actions_history.add_pending_task(task_id, task)

            self._queue_changed.emit()

    @classmethod
    def _dns_domains_count(cls, dns_tasks: List[DnsRefreshTask]) -> int:
        return sum([len(task.dns_items) for task in dns_tasks])

    @pyqtSlot(DeployWalletTask)
    @slot_exc_handler()
    def on_deploy_task(self, task: DeployWalletTask):
        self._show_notification(f'Init {task.record.name} wallet', "Sending transaction")

        with self.busy_context():
            wallet = task.wallet
            task_id = self._ctx.ton_daemon.deploy_wallet(wallet)
            self._actions_history.add_pending_task(task_id, task)

        self._queue_changed.emit()

    @pyqtSlot(object)
    @slot_exc_handler()
    def on_response_from_daemon(self, response: TonDaemonResponse):
        if isinstance(response, TonDaemonResult):
            self._broadcast_task_complete(response)
        elif isinstance(response, TonDaemonTaskTaken):
            self._task_taken(response)
        elif isinstance(response, TonDaemonGoodbye):
            self.daemon_observer.restart()
        elif isinstance(response, TonDaemonDeathNote):
            self._daemon_is_dead()
        else:
            raise NotImplementedError

    def _task_taken(self, response: TonDaemonTaskTaken):
        self._actions_history.set_pending_task_taken(response.task_id)
        self._queue_changed.emit()

    def _broadcast_task_complete(self, response: TonDaemonResult):
        broadcast_task = self._actions_history.get_pending_task(response.task_id)
        broadcast_result = response.broadcast_result
        self._notify_broadcast_result(broadcast_task, broadcast_result)
        self._actions_history.add_broadcast_result(response.task_id,
                                                   BroadcastTaskResult.from_broadcast_task(broadcast_task,
                                                                                           response))
        self._actions_history.remove_pending_task(response.task_id)
        self._queue_changed.emit()

    @pyqtSlot(ExportWalletTask)
    @slot_exc_handler()
    def on_export_wallet(self, task: ExportWalletTask):
        self._reset_notification()
        with self.busy_context():
            try:
                self._export_wallet(task)
            except StorageError as exception:
                self._error.emit(
                    ErrorNotification(
                        title="Storage error",
                        exception=exception
                    )
                )
            except Exception as exception:
                self._error.emit(
                    ErrorNotification(
                        exception=exception,
                        critical=True
                    )
                )

    @pyqtSlot(uuid.UUID)
    @slot_exc_handler()
    def on_cancel_broadcast_task(self, task_id: uuid.UUID):
        self._ctx.ton_daemon.cancel_task(task_id)
        self._actions_history.set_pending_task_cancelled(task_id)
        self._queue_changed.emit()

    def _export_wallet(self, task: ExportWalletTask):
        addr_filename = task.record.name + ".addr"
        pk_filename = task.record.name + ".pk"
        addr_path = os.path.join(task.destination_dir, addr_filename)
        pk_path = os.path.join(task.destination_dir, pk_filename)

        addr = Address(task.record.address).to_buffer()
        pk = task.secret.private_key[:32]

        storage.save_bytes(addr_path, addr)
        storage.save_bytes(pk_path, pk)

        title = f"Wallet exported"
        message = f"Saved as {addr_filename}, {pk_filename}"

        self._show_notification(title, message, True)

    def _notify_broadcast_result(self, broadcast_task: BroadcastTask,
                                 broadcast_result: Union[BroadcastResult, TonError]):
        if isinstance(broadcast_task, TransferTask):
            amount = f'all coins' if broadcast_task.transfer_all_coins else f'{broadcast_task.amount} TON'
            titles = [f'Transfer {amount} to {broadcast_task.recipient.name}']
        elif isinstance(broadcast_task, DeployWalletTask):
            titles = [f'Init {broadcast_task.record.name} wallet']
        elif isinstance(broadcast_task, DnsRefreshTask):
            domains = [f'{domain}.ton' for domain in broadcast_task.dns_domains]
            titles = [f'Refresh {domain}' for domain in domains]
        else:
            raise NotImplementedError

        message = str(broadcast_result)
        good = isinstance(broadcast_result, BroadcastResult) and broadcast_result.status != BroadcastStatusEnum.failed

        for title in titles:
            self._show_notification(title, message, good)

    def _daemon_is_dead(self):
        self._error.emit(ErrorNotification(
            message='Broadcast daemon is dead',
            critical=True
        ))

    def _show_notification(self, title: str, message: str, good: Optional[bool] = None):
        system_notification = SystemNotification(
            title=title,
            message=message,
            good=good
        )
        self._system_notify.emit(system_notification)

    def _reset_notification(self):
        self._system_notify.emit(SystemNotification(title='', message='', reset=True))

    def network_is_tesnet(self) -> bool:
        return self._ctx.config.provider.dapp.network == TonNetworkEnum.testnet

    def task_is_taken(self, task_id: uuid.UUID) -> bool:
        return self._actions_history.task_is_taken(task_id)

    def task_is_cancelled(self, task_id: uuid.UUID) -> bool:
        return self._actions_history.task_is_cancelled(task_id)


class BroadcastDaemonObserver(QObject):
    UPDATE_INTERVAL_MS = 500
    got_response = pyqtSignal(object)  # TonDaemonResponse

    def __init__(self, ton_daemon: TonDaemon):
        super().__init__()
        self._ton_daemon = weakref.proxy(ton_daemon)
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run)
        self._timer = self._setup_timer()

    def _setup_timer(self) -> QTimer:
        timer = QTimer()
        timer.setInterval(self.UPDATE_INTERVAL_MS)
        timer.timeout.connect(self._update)
        self._thread.finished.connect(timer.stop)
        timer.moveToThread(self._thread)
        return timer

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.quit()
        self._thread.wait()

    def restart(self):
        self._thread.quit()
        self._thread.wait()
        self._thread.start()

    def __del__(self):
        try:
            running = self._thread.isRunning()
        except RuntimeError:  # (C++ object has been deleted)
            running = False

        log = tons_logger().error if running else tons_logger().debug
        log(f'daemon observer deleted ({running=})')

    @pyqtSlot()
    @slot_exc_handler()
    def _run(self):
        self._timer.timeout.emit()
        self._timer.start()

    @pyqtSlot()
    @slot_exc_handler()
    def _update(self):
        try:
            result: TonDaemonResponse = self._ton_daemon.results_queue.get(False)
            tons_logger().debug(f'got daemon response: {result}')
            self.got_response.emit(result)
        except queue.Empty:
            pass
        except ReferenceError:
            tons_logger().warning('reference error in daemon observer')

