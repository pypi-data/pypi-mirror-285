import decimal
import time
from copy import deepcopy
from datetime import datetime
from enum import Enum
from functools import wraps
from threading import Thread, Lock
from typing import Union, Dict, Optional, List, Sequence
from uuid import UUID

from colorama import Fore
from pydantic import BaseModel, Field

from tons.logging_ import tons_logger
from tons.tonclient._client._base import TonDaemonResult, BroadcastResult, BroadcastStatusEnum, \
    NftItemInfoResult, JettonMinterResult, jetton_amount_to_readable, AddressInfoResult, AddressState, \
    TonDaemonGoodbye, TonDaemonDeathNote, FailedToParseDataCell, TonDaemonTaskTaken
from tons.tonclient._exceptions import TonError, TonDappError
from tons.tonsdk.contract.wallet import WalletContract, SendModeEnum, InternalMessage, MultiSigWalletContractV2, \
    MultiSigTransferRequest, get_multisig_order_address, MultiSigUpdateRequest
from tons.tonsdk.utils import Address, TonCurrencyEnum
from tons.ui._utils import shorten_dns_domain, SharedObject


class BackgroundTaskError(TonDappError):
    pass


class BackgroundTaskCritical(Exception):
    pass


class BackgroundTaskEnum(str, Enum):
    transfer = 'transfer'
    dns_refresh = 'dns_refresh'
    jetton_transfer = 'jetton_transfer'


class BackgroundTask(BaseModel):
    is_pending: bool = True
    result: Optional[TonDaemonResult] = None
    result_description: Union[str, List[str]] = ''
    result_is_bad: bool = False
    time_start: datetime = Field(default_factory=datetime.now)
    time_finish: Optional[datetime] = None

    @property
    def description(self) -> Union[str, List[str]]:
        raise NotImplementedError

    def set_result_bad(self):
        self.result_is_bad = True

        if isinstance(self.result_description, str):
            self.result_description = self.__result_description_bad(self.result_description)
        else:
            self.result_description = list(map(self.__result_description_bad, self.result_description))

    @classmethod
    def __result_description_bad(cls, result_description: str) -> str:
        if result_description.startswith(Fore.RED):
            return result_description
        result_description = Fore.RED + result_description + Fore.RESET
        return result_description

    @property
    def _descriptions_count(self) -> int:
        n = 1
        if not isinstance(self.description, str):
            n = max(n, len(self.description))

        if not isinstance(self.result_description, str):
            n = max(n, len(self.result_description))

        return n

    @property
    def descriptions(self) -> List[str]:
        if isinstance(self.description, str):
            return [self.description] * self._descriptions_count
        return self.description

    @property
    def result_descriptions(self) -> List[str]:
        if isinstance(self.result_description, str):
            return [self.result_description] * self._descriptions_count
        return self.result_description


class TransferBackgroundTask(BackgroundTask):
    amount: decimal.Decimal
    src_addr: Address
    dst_addr: Address
    transfer_all: bool

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self) -> str:
        if self.transfer_all:
            _amount = 'all remaining coins'
        else:
            _amount = f'{self.amount} TON'
        return f'Transfer {_amount} from {self.src_addr.to_mask()} to {self.dst_addr.to_mask()}'


class DNSRefreshBackgroundTask(BackgroundTask):
    dns_items: List[NftItemInfoResult]

    @property
    def description(self) -> List[str]:
        domains = (f'{shorten_dns_domain(dns.dns_domain)}.ton' for dns in self.dns_items)

        return [f'Refresh {domain}' for domain in domains]


class JettonTransferBackgroundTask(BackgroundTask):
    symbol: str
    amount_readable: decimal.Decimal
    src_addr: Address
    dst_addr: Address

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self):
        return f'Transfer ' \
               f'{self.amount_readable} ' \
               f'{self.symbol if self.symbol else "UNKNOWN"} ' \
               f'from {self.src_addr.to_mask()} ' \
               f'to {self.dst_addr.to_mask()}'


class DeployWalletBackgroundTask(BackgroundTask):
    wallet_addr: Address

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self):
        return f'Init wallet {self.wallet_addr.to_mask()}'


class DeployMultisigBackgroundTask(BackgroundTask):
    multisig_addr: Address
    deployer_addr: Address

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self):
        return f'Deploy multisig {self.multisig_addr.to_mask()}'


class DeployOrderBackgroundTask(BackgroundTask):
    order_addr: Address
    multisig_addr: Address

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self):
        return f'Place order {self.order_addr.to_mask()} for multisig {self.multisig_addr.to_mask()}'


class ApproveOrderBackgroundTask(BackgroundTask):
    order_addr: Address
    signer_addr: Address

    class Config:
        arbitrary_types_allowed = True

    @property
    def description(self):
        return f'Approve order {self.order_addr.to_mask()} by {self.signer_addr.to_mask()}'


def _require_thread_alive(method):
    @wraps(method)
    def magic(self, *args, **kwargs):
        if not self._thread.is_alive():
            raise BackgroundTaskCritical("Background task manager is dead")
        return method(self, *args, **kwargs)
    return magic


class BackgroundTaskManager:
    def __init__(self, ctx: SharedObject):
        self.ctx = ctx

        self._tasks: Dict[UUID, BackgroundTask] = dict()
        self._thread = None

        self._tasks_access_lock = Lock()

    @_require_thread_alive
    def transfer_task(self, from_wallet: WalletContract, to_addr: str,
                      amount: Union[int, str, decimal.Decimal], payload=None,
                      send_mode=SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately,
                      state_init=None) -> UUID:
        with self._tasks_access_lock:
            messages = [InternalMessage(
                to_addr=Address(to_addr),
                amount=amount,
                send_mode=send_mode,
                body=payload,
                currency=TonCurrencyEnum.ton,
                state_init=state_init,
            )]
            task_id = self.ctx.ton_daemon.transfer(from_wallet, messages)
            self._tasks[task_id] = TransferBackgroundTask(amount=amount,
                                                          transfer_all=bool(send_mode &
                                                                            SendModeEnum.carry_all_remaining_balance),
                                                          src_addr=from_wallet.address, dst_addr=Address(to_addr))
        return task_id

    @_require_thread_alive
    def dns_refresh_task(self, from_wallet: WalletContract, dns_items: Sequence[NftItemInfoResult]) -> UUID:
        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.refresh_dns_ownership(from_wallet, dns_items)
            self._tasks[task_id] = DNSRefreshBackgroundTask(dns_items=dns_items)
        return task_id

    @_require_thread_alive
    def jetton_transfer_task(self, jetton_minter_info: JettonMinterResult, from_wallet: WalletContract,
                             from_jetton_wallet_addr: Address, to_address: Address,
                             jetton_amount: int, gas_amount: decimal.Decimal) \
            -> UUID:

        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.jetton_transfer(from_wallet, from_jetton_wallet_addr, to_address,
                                                          jetton_amount,
                                                          gas_amount)
            self._tasks[task_id] = JettonTransferBackgroundTask(
                amount_readable=jetton_amount_to_readable(jetton_amount, jetton_minter_info.metadata),
                symbol=jetton_minter_info.metadata.symbol or '',
                src_addr=from_wallet.address,
                dst_addr=to_address
            )
        return task_id

    @_require_thread_alive
    def deploy_wallet_task(self, wallet: WalletContract) -> UUID:
        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.deploy_wallet(wallet)
            self._tasks[task_id] = DeployWalletBackgroundTask(wallet_addr=Address(wallet.address))
        return task_id

    @_require_thread_alive
    def deploy_multisig_task(self, from_wallet: WalletContract, contract: MultiSigWalletContractV2) -> UUID:
        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.deploy_multisig(from_wallet, contract)
            self._tasks[task_id] = DeployMultisigBackgroundTask(multisig_addr=Address(contract.address),
                                                                deployer_addr=Address(from_wallet.address))
        return task_id

    @_require_thread_alive
    def deploy_order_task(self, from_wallet: WalletContract,
                          actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]],
                          expiration_date: int, is_signer: bool, address_idx: int, order_id: int,
                          multisig_address: Union[Address, str]) -> UUID:
        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.deploy_order(from_wallet, actions, expiration_date, is_signer, address_idx,
                                                       order_id, multisig_address)
            order_addr = get_multisig_order_address(Address(multisig_address), order_id)
            self._tasks[task_id] = DeployOrderBackgroundTask(order_addr=order_addr,
                                                             multisig_addr=Address(multisig_address))
        return task_id

    @_require_thread_alive
    def approve_order_task(self, from_wallet: WalletContract, signer_idx: int,
                           order_address: Union[str, Address]) -> UUID:
        with self._tasks_access_lock:
            task_id = self.ctx.ton_daemon.approve_order(from_wallet, signer_idx, order_address)
            self._tasks[task_id] = ApproveOrderBackgroundTask(order_addr=Address(order_address),
                                                              signer_addr=Address(from_wallet.address))
        return task_id

    def start(self):
        if self._thread is not None:
            while self._thread.is_alive():
                ...
        # The thread runs until it receives a goodbye message from the broadcast daemon
        self._thread = Thread(target=self._run, daemon=True, name="Background task manager")
        self._thread.start()

    @_require_thread_alive
    def tasks_list(self, unsafe=False) -> List[BackgroundTask]:
        """
        :param unsafe: if True, mutex lock is not used, might return inconsistent data
        :return: list of background tasks
        """
        if unsafe:
            return self.__tasks_list()
        with self._tasks_access_lock:
            return self.__tasks_list()

    def __tasks_list(self):
        return sorted([deepcopy(task) for task in self._tasks.values()], key=lambda t: t.time_start)

    @property
    @_require_thread_alive
    def tasks_list_empty(self) -> bool:
        return len(self._tasks) == 0

    @_require_thread_alive
    def get_task(self, task_id: UUID) -> BackgroundTask:
        with self._tasks_access_lock:
            return deepcopy(self._tasks[task_id])

    def _run(self):
        while True:
            r = self.ctx.ton_daemon.results_queue.get()
            if isinstance(r, TonDaemonGoodbye):
                break
            if isinstance(r, TonDaemonDeathNote):
                break  # TODO: pass exceptions to the main thread
                # raise r.exception
            elif isinstance(r, TonDaemonResult):
                pass
            elif isinstance(r, TonDaemonTaskTaken):
                continue
            else:
                break  # TODO: pass exceptions to the main thread
                # raise TypeError(f"Unexpected result from TON daemon: {r}")

            with self._tasks_access_lock:
                self._tasks[r.task_id].is_pending = False
                self._tasks[r.task_id].time_finish = datetime.now()
                self._tasks[r.task_id].result = r
                self.finalize(self._tasks[r.task_id])

    @property
    @_require_thread_alive
    def unfinished_tasks_remaining(self):
        with self._tasks_access_lock:
            return any([t.is_pending for t in self._tasks.values()])

    @_require_thread_alive
    def finalize(self, task: BackgroundTask):
        if task.result is not None:
            if not isinstance(task.result.broadcast_result, BroadcastResult):
                task.result_description = f'{task.result.broadcast_result}'
                task.set_result_bad()
                return

            bcr = task.result.broadcast_result
            task.result_description = f'{bcr.status}'

            if bcr.status == BroadcastStatusEnum.failed:
                task.set_result_bad()

            if isinstance(task, DNSRefreshBackgroundTask):
                self._finalize_dns_refresh_task(task)

            if isinstance(task, DeployWalletBackgroundTask):
                self._finalize_deploy_wallet_task(task)

            # if isinstance(task, DeployMultisigBackgroundTask):
            #     self._finalize_deploy_multisig_task(task)
            #
            # if isinstance(task, DeployOrderBackgroundTask):
            #     self._finalize_deploy_order_task(task)

    def _finalize_deploy_order_task(self, task: DeployOrderBackgroundTask):
        # TODO analyze transactions
        bcr = task.result.broadcast_result
        if bcr.status != BroadcastStatusEnum.failed:
            try:
                _, order_info = \
                    self.ctx.ton_client.get_multisig_order_information(task.order_addr)
            except (TonError, FailedToParseDataCell):
                pass
            else:
                task.result_description = "order placed"
                if task.multisig_addr != Address(order_info.multisig_address):
                    # This should not happen and signifies seriously broken logic either on blockchain or in tons
                    task.result_description = "multisig address does not match"
                    task.set_result_bad()

    def _finalize_deploy_multisig_task(self, task: DeployMultisigBackgroundTask):
        # TODO analyze transactions
        bcr = task.result.broadcast_result
        if bcr.status != BroadcastStatusEnum.failed:
            try:
                _, multisig_info = \
                    self.ctx.ton_client.get_multisig_information(task.multisig_addr)
            except (TonError, FailedToParseDataCell):
                pass
            else:
                task.result_description = "multisig deployed"

    def _finalize_deploy_wallet_task(self, task: DeployWalletBackgroundTask):
        bcr = task.result.broadcast_result
        assert isinstance(bcr, BroadcastResult)
        if bcr.status != BroadcastStatusEnum.failed:
            try:
                updated_address_info: AddressInfoResult = \
                    self.ctx.ton_client.get_address_information(task.wallet_addr.to_string())
            except TonError as e:
                task.result_description = \
                    f"{bcr.status} but failed to verify: " + str(e)
                task.set_result_bad()
            else:
                if updated_address_info.state == AddressState.active:
                    task.result_description = 'wallet initialized'
                else:
                    task.result_description = 'failed to init wallet'
                    task.set_result_bad()

    class _FailedToVerifyDnsRefreshSuccess(Exception):
        pass

    def _finalize_dns_refresh_task(self, task: DNSRefreshBackgroundTask, retries: int = 5, sleep_time: int = 15):
        bcr = task.result.broadcast_result
        assert isinstance(bcr, BroadcastResult)
        if bcr.status != BroadcastStatusEnum.failed:
            task.result_description = [''] * len(task.dns_items)
            for idx, dns in enumerate(task.dns_items):
                for retry_id in range(retries):
                    try:
                        self._verify_dns_refreshment(dns, idx, task)
                    except self._FailedToVerifyDnsRefreshSuccess as exc:
                        tons_logger().error(f"failed to verify dns refresh, {retry_id=}", exc_info=exc)
                        time.sleep(sleep_time)
                        continue
                    else:
                        break
                else:
                    task.result_description[idx] = f"ownership update {bcr.status} but failed to verify success, " \
                                                   f"please check the domain status manually"
                    task.set_result_bad()

            assert len(task.result_description) == len(task.dns_items)

    def _verify_dns_refreshment(self, dns: NftItemInfoResult, idx: int,
                                task: DNSRefreshBackgroundTask):
        try:
            updated_dns_info: NftItemInfoResult = \
                self.ctx.ton_client.get_dns_domain_information(dns.dns_domain)
        except TonError as e:
            raise self._FailedToVerifyDnsRefreshSuccess(str(e))
        else:
            if updated_dns_info.dns_last_fill_up_time > dns.dns_last_fill_up_time:
                task.result_description[idx] = \
                    f"refreshed (expires " \
                    f"{datetime.utcfromtimestamp(updated_dns_info.dns_expires)} GMT)"
            else:
                raise self._FailedToVerifyDnsRefreshSuccess


