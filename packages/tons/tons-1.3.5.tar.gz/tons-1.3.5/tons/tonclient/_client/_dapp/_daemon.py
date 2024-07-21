import decimal
import uuid
from queue import SimpleQueue
from threading import Thread, Lock
from typing import Union, Dict, List, Sequence, Set

from tons.config import Config
from tons.logging_ import tons_logger
from tons.tonclient import DAppTonClient
from tons.tonclient._client._base import BroadcastResult, TonDaemon, TonDaemonResult, DaemonTask, DaemonTaskNameEnum, \
    NftItemInfoResult, TonDaemonGoodbye, TonDaemonDeathNote, TonDaemonResponse, TonDaemonTaskTaken, TransactionCanceled, \
    TonDaemonResultCancelled
from tons.tonclient._exceptions import TonError
from tons.tonsdk.contract.wallet import WalletContract, InternalMessage, MultiSigWalletContractV2, \
    MultiSigTransferRequest, MultiSigUpdateRequest
from tons.tonsdk.utils import Address


class DAppBroadcastDaemon(TonDaemon):
    def __init__(self, config: Config, client: DAppTonClient):
        self._results_queue: SimpleQueue[TonDaemonResponse] = SimpleQueue()
        self.config = config
        self._client = client
        self._is_running = False
        self._thread = None
        self._tasks_queue: SimpleQueue[DaemonTask] = SimpleQueue()
        self._cancelled_tasks: Set[uuid.UUID] = set()
        self._cancel_lock = Lock()

    def __del__(self):
        tons_logger().debug('Broadcast daemon deleted')

    def start(self):
        if self._thread is not None:
            raise RuntimeError('Broadcast daemon thread already exists.')

        self._is_running = True
        self._thread = Thread(target=self._run_background_tasks, daemon=True, name='DApp Broadcast Daemon')
        self._thread.start()

    def stop(self):
        """
        Stop the daemon, but wait until it finishes the current tasks.
        """
        if self._thread is None:
            raise RuntimeError('Broadcast daemon thread does not exist.')

        self._is_running = False
        self._tasks_queue.put(DaemonTask(task_name=DaemonTaskNameEnum.stop, kwargs=dict()))
        while self._thread.is_alive():
            ...
        self._thread = None

    def transfer(self, from_wallet: WalletContract, messages: List[InternalMessage]) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.transfer, locals())

    def refresh_dns_ownership(self, from_wallet: WalletContract, dns_items: Sequence[NftItemInfoResult]) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.refresh_dns, locals())

    def jetton_transfer(self, from_wallet: WalletContract, from_jetton_wallet_addr: Address,
                        to_address: Address, jetton_amount: int, gas_amount: decimal.Decimal) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.jetton_transfer, locals())

    def deploy_wallet(self, wallet: WalletContract) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.deploy_wallet, locals())

    def deploy_multisig(self, from_wallet: WalletContract,
                        contract: MultiSigWalletContractV2) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.deploy_multisig, locals())

    def deploy_order(self, from_wallet: WalletContract,
                           actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]],
                           expiration_date: int, is_signer: bool, address_idx: int, order_id: int,
                           multisig_address: Union[Address, str]) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.deploy_order, locals())

    def approve_order(self, from_wallet: WalletContract, signer_idx: int,
                      order_address: Union[str, Address]) -> uuid.UUID:
        return self._add_task(DaemonTaskNameEnum.approve_order, locals())

    def _add_task(self, task_name: DaemonTaskNameEnum, kwargs: Dict) -> uuid.UUID:
        kwargs = {k: v for k, v in kwargs.items() if k != 'self'}
        if not kwargs.get('wait_for_result', True):
            raise RuntimeError("wait_for_result must be set to True for tasks running inside Broadcast Daemon")
        kwargs['wait_for_result'] = True
        task = DaemonTask(task_name=task_name, kwargs=kwargs)
        self._tasks_queue.put(task)
        return task.task_id

    def _run_background_tasks(self):
        try:
            while self._is_running:
                task = self._tasks_queue.get()
                if task.task_name == DaemonTaskNameEnum.stop:
                    break

                if task.task_id in self._cancelled_tasks:
                    self._results_queue.put(TonDaemonResultCancelled(task_id=task.task_id))
                    with self._cancel_lock:
                        self._cancelled_tasks.discard(task.task_id)
                    continue

                self._results_queue.put(TonDaemonTaskTaken(task_id=task.task_id))
                task_result = self._perform_task(task)
                self._results_queue.put(TonDaemonResult(task_id=task.task_id, broadcast_result=task_result))

        except Exception as exception:
            tons_logger().error(f'Broadcast daemon dead. Death note: {type(exception).__name__}', exc_info=exception)
            self._results_queue.put(TonDaemonDeathNote(exception=exception))
        else:
            self._results_queue.put(TonDaemonGoodbye())
        self._is_running = False

    def _perform_task(self, task: DaemonTask) -> Union[BroadcastResult, TonError]:
        methods_map = {DaemonTaskNameEnum.transfer: self._client.transfer,
                       DaemonTaskNameEnum.jetton_transfer: self._client.jetton_transfer,
                       DaemonTaskNameEnum.deploy_wallet: self._client.deploy_wallet,
                       DaemonTaskNameEnum.refresh_dns: self._client.refresh_dns_ownership,

                       DaemonTaskNameEnum.deploy_multisig: self._client.deploy_multisig,
                       DaemonTaskNameEnum.deploy_order: self._client.deploy_multisig_order,
                       DaemonTaskNameEnum.approve_order: self._client.approve_multisig_order}
        try:
            try:
                method = methods_map[task.task_name]
            except KeyError:
                raise NotImplementedError(f"{task.task_name} not supported")
            else:
                _, result = method(**task.kwargs)
                return result
        except TonError as e:
            tons_logger().info(f'TonError caught in _perform_task: {e}')
            tons_logger().debug(msg='', exc_info=e)
            return e

    @property
    def results_queue(self) -> SimpleQueue:
        assert self._thread.is_alive(), "Thread is dead"
        return self._results_queue

    def cancel_task(self, task_id: uuid.UUID):
        """
        ! No guarantee that the task will be cancelled if it is already taken.
        The UI should watch the results_queue for TonDaemonTaskTaken,
        and only allow the user to cancel those that are not taken.

        ! Do not put task_id's of tasks that have not been queued
        or already have been cancelled as it will cause a small unnecessary memory leak
        """

        with self._cancel_lock:
            self._cancelled_tasks.add(task_id)


def _exclude_self(params: Dict):
    return {k: v for k, v in params.items() if k != 'self'}
