import decimal
from datetime import datetime
from decimal import Decimal
from typing import Union, List, Optional, Tuple, Sequence

from pydantic import BaseModel, Field, validator

from tons.tonclient._client._base import TonDaemonResult, AddressInfoResult, NftItemInfoResult, BroadcastResult, \
    TransactionHashNotFound
from tons.tonclient.utils import BaseKeyStore, Record, WhitelistContact, WalletSecret, get_wallet_from_record_and_secret
from tons.tonsdk.boc import Cell
from tons.tonsdk.contract.wallet import SendModeEnum, InternalMessage, Wallets, WalletContract, WalletVersionEnum
from tons.tonsdk.crypto._payload_encryption import encrypt_message
from tons.tonsdk.utils import Address, TonCurrencyEnum


class BaseTaskModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        frozen = True


class BroadcastTask(BaseTaskModel):
    time_start: datetime = Field(default_factory=datetime.now)


class EditAndRetryInfo(BaseModel):
    @classmethod
    def from_broadcast_task(cls, task: BroadcastTask) -> Optional['EditAndRetryInfo']:
        if isinstance(task, TransferTask):
            return task.edit_and_retry_info


class TransferEditAndRetryInfo(EditAndRetryInfo):
    amount: decimal.Decimal
    keystore_name: str
    src: Address
    dst: Address
    comment: str
    encrypt_comment: bool
    state_init_path: str
    body_path: str
    transfer_all_coins: bool
    destroy_if_zero: bool

    class Config:
        arbitrary_types_allowed = True


class TransferTask(BroadcastTask):
    secret: WalletSecret
    sender: Record
    recipient: WhitelistContact
    amount: Decimal
    message: Optional[str]
    state_init: Optional[Cell]
    body: Optional[Cell]
    encrypt_message: bool
    receiver_info: Optional[AddressInfoResult]
    transfer_all_coins: bool
    destroy_if_zero: bool

    edit_and_retry_info: TransferEditAndRetryInfo

    class Config:
        arbitrary_types_allowed = True

    @property
    def send_mode(self) -> int:
        send_mode = SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately
        if self.destroy_if_zero:
            send_mode |= SendModeEnum.destroy_account_if_zero
        if self.transfer_all_coins:
            send_mode |= SendModeEnum.carry_all_remaining_balance
        return send_mode

    @property
    def wallet(self) -> WalletContract:
        return get_wallet_from_record_and_secret(self.sender, self.secret)

    @property
    def transfer_message(self) -> InternalMessage:
        message = self.message
        if self.encrypt_message:
            assert not self.body and message and self.receiver_info
            message = encrypt_message(message, self.secret.public_key, self.receiver_info.public_key,
                                      self.secret.private_key, self.wallet.address)

        return InternalMessage(
            to_addr=Address(self.recipient.address),
            send_mode=self.send_mode,
            amount=self.amount,
            body=message or self.body,
            state_init=self.state_init,
            currency=TonCurrencyEnum.ton
        )


class DnsRefreshTask(BroadcastTask):
    secret: WalletSecret
    sender: Record
    dns_items: Sequence[NftItemInfoResult]

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    @property
    def wallet(self) -> WalletContract:
        return get_wallet_from_record_and_secret(self.sender, self.secret)

    @validator("dns_items", always=True)
    def _validate_dns_items(cls, v: Sequence[NftItemInfoResult], values):
        if not (1 <= len(v) <= 4):
            raise ValueError('1 to 4 DNS can be refreshed within one transaction')

        for dns_item in v:
            if dns_item.dns_domain is None:
                raise ValueError('DNS domain should not be None')

            if (dns_item.account is None) or (dns_item.account.address is None):
                raise ValueError('DNS account addresses should be valid')

        return v

    @property
    def dns_domains(self) -> Sequence[str]:
        return tuple(dns_item.dns_domain for dns_item in self.dns_items)

    @property
    def dns_domain_addresses(self) -> Sequence[Address]:
        return tuple(Address(dns_item.account.address) for dns_item in self.dns_items)


class CreateBatchWalletTask(BaseTaskModel):
    version: WalletVersionEnum
    workchain: int
    from_idx: int
    to_idx: int
    prefix: str
    suffix: str
    comment: str


class DeployWalletTask(BroadcastTask):
    secret: WalletSecret
    record: Record

    @property
    def wallet(self) -> WalletContract:
        return get_wallet_from_record_and_secret(self.record, self.secret)


class ExportWalletTask(BaseTaskModel):
    record: Record
    destination_dir: str
    secret: WalletSecret


class TaskResultPayload(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        frozen = True


class TransferResultPayload(TaskResultPayload):
    amount: Decimal
    transfer_all_coins: bool
    src_addr: str
    dst_addr: str

    @classmethod
    def from_broadcast_task(cls, task: TransferTask) -> 'TransferResultPayload':
        return cls(amount=task.amount, transfer_all_coins=task.transfer_all_coins,
                   src_addr=task.sender.tep_standard_user_address, dst_addr=task.recipient.address)


class DnsResultPayload(TaskResultPayload):
    domains: List[str]

    @classmethod
    def from_broadcast_task(cls, task: DnsRefreshTask) -> 'DnsResultPayload':
        return cls(domains=list(task.dns_domains))


class DeployWalletResultPayload(TaskResultPayload):
    wallet_name: str
    wallet_addr: str

    @classmethod
    def from_broadcast_task(cls, task: DeployWalletTask) -> 'DeployWalletResultPayload':
        return cls(wallet_name=task.record.name, wallet_addr=task.record.tep_standard_user_address)


class BroadcastTaskResult(BaseTaskModel):
    result: TonDaemonResult
    result_payload: TaskResultPayload
    time_start: datetime
    time_finish: datetime = Field(default_factory=datetime.now)
    edit_and_retry_info: Optional[EditAndRetryInfo]

    @classmethod
    def from_broadcast_task(cls, broadcast_task: BroadcastTask,
                            result: TonDaemonResult) -> 'BroadcastTaskResult':
        if isinstance(broadcast_task, TransferTask):
            result_payload = TransferResultPayload.from_broadcast_task(broadcast_task)
        elif isinstance(broadcast_task, DnsRefreshTask):
            result_payload = DnsResultPayload.from_broadcast_task(broadcast_task)
        elif isinstance(broadcast_task, DeployWalletTask):
            result_payload = DeployWalletResultPayload.from_broadcast_task(broadcast_task)
        else:
            raise ValueError("Invalid broadcast_task type: ", type(broadcast_task))

        return cls(
            result=result,
            result_payload=result_payload,
            time_start=broadcast_task.time_start,
            edit_and_retry_info=EditAndRetryInfo.from_broadcast_task(broadcast_task)
        )

    def transaction_hash(self) -> Optional[str]:
        broadcast_result = self.result.broadcast_result
        if not isinstance(broadcast_result, BroadcastResult):
            return
        try:
            return broadcast_result.transaction_hash()
        except TransactionHashNotFound:
            return
