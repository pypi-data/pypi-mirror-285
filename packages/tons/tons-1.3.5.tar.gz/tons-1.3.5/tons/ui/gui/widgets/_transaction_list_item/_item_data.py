import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Union, Sequence, List

from tons.tonclient import TonError, BroadcastStatusEnum
from tons.tonclient._client._base import TransactionInfo
from tons.tonsdk.utils import Address
from tons.ui.gui.utils import TransferTask, DnsRefreshTask, DeployWalletTask, BroadcastTask, BroadcastTaskResult, \
    TransferResultPayload, DnsResultPayload, DeployWalletResultPayload, html_text_colored, pretty_balance, \
    html_text_font, TaskResultPayload, EditAndRetryInfo
from ._colors import TransactionColors
from ._fonts import TransactionFonts
from .._base import AbstractListItemModel
from ...services.tx_info_service import transaction_info


class TransactionListItemKind(Enum):
    complete = auto()
    pending = auto()
    planned = auto()
    error = auto()


class TransactionButton(Enum):
    view_in_scanner = auto()
    edit_and_retry = auto()
    cancel = auto()


class TransactionListItemData(AbstractListItemModel):
    kind: TransactionListItemKind
    description: str  # todo: rich string with html?
    error: Optional[str]
    time_start: datetime
    time_finish: Optional[datetime]
    button_to_display: Optional[TransactionButton]
    edit_and_retry_info: Optional[EditAndRetryInfo]
    tx_hash: Optional[str]
    tx_info: Optional[TransactionInfo]
    task_id: Optional[uuid.UUID]
    taken: bool

    def __eq__(self, other: Optional['TransactionListItemData']):
        if other is None:
            return False

        return self.kind == other.kind \
               and self.description == other.description \
               and self.time_start == other.time_start \
               and self.time_finish == other.time_finish \
               and self.task_id == other.task_id \
               and self.tx_hash == other.tx_hash

    @classmethod
    def from_background_transaction(cls, background_tx: Union[BroadcastTask, BroadcastTaskResult],
                                    taken: bool = True, task_id: Optional[uuid.UUID] = None) \
            -> List['TransactionListItemData']:
        error = None
        tx_hash = None
        tx_info = None
        button_to_display = None
        edit_and_retry_info = None

        if isinstance(background_tx, BroadcastTask):
            time_start = background_tx.time_start
            time_finish = None

            if isinstance(background_tx, TransferTask):
                description = cls._description(TransferResultPayload.from_broadcast_task(background_tx))
            elif isinstance(background_tx, DnsRefreshTask):
                description = cls._description(DnsResultPayload.from_broadcast_task(background_tx))
            elif isinstance(background_tx, DeployWalletTask):
                description = cls._description(DeployWalletResultPayload.from_broadcast_task(background_tx))
            else:
                raise ValueError(f"Unknown background_tx kind: {type(background_tx)}")

            kind = TransactionListItemKind.pending
            if not taken:
                button_to_display = TransactionButton.cancel
                kind = TransactionListItemKind.planned

        elif isinstance(background_tx, BroadcastTaskResult):
            time_start = background_tx.time_start
            time_finish = background_tx.time_finish
            description = cls._description(background_tx.result_payload)
            if isinstance(background_tx.result.broadcast_result, TonError) \
                    or background_tx.result.broadcast_result.status == BroadcastStatusEnum.failed:
                kind = TransactionListItemKind.error
                error = str(background_tx.result.broadcast_result)
            else:
                kind = TransactionListItemKind.complete
            tx_hash = background_tx.transaction_hash()
            edit_and_retry_info = background_tx.edit_and_retry_info

            if kind == TransactionListItemKind.complete:
                if tx_hash:
                    tx_info = transaction_info(tx_hash)
                    if tx_info:
                        button_to_display = TransactionButton.view_in_scanner
            elif kind == TransactionListItemKind.error:
                if edit_and_retry_info:
                    button_to_display = TransactionButton.edit_and_retry

        else:
            raise ValueError("Unknown background_tx kind")

        return [
            cls(kind=kind,
                description=desc,
                error=error,
                time_start=time_start,
                time_finish=time_finish,
                button_to_display=button_to_display,
                tx_hash=tx_hash,
                tx_info=tx_info,
                edit_and_retry_info=edit_and_retry_info,
                task_id=task_id,
                taken=taken)
            for desc in description
        ]

    @classmethod
    def _description(cls, payload: TaskResultPayload) -> List[str]:
        if isinstance(payload, TransferResultPayload):
            if payload.transfer_all_coins:
                amount = "all remaining coins"
            else:
                amount = pretty_balance(payload.amount, gray_decimal_part=False)
                amount = html_text_colored(amount, TransactionColors().highlight)
                amount = html_text_font(amount, family=TransactionFonts().mono.family())

            src = cls._formatted_address(payload.src_addr)
            dst = cls._formatted_address(payload.dst_addr)

            return [f"Transfer {amount} from {src} to {dst}"]
        elif isinstance(payload, DnsResultPayload):
            domains = [cls._formatted_domain(domain) for domain in payload.domains]
            return [f"Refresh {domain}" for domain in domains]
        elif isinstance(payload, DeployWalletResultPayload):
            wallet = cls._formatted_wallet_name(payload.wallet_name)
            addr = cls._formatted_address(payload.wallet_addr)
            return [f"Deploy {wallet} ({addr})"]
        else:
            raise ValueError(f"Unknown payload {type(payload)}")

    @classmethod
    def _formatted_address(cls, addr: str) -> str:
        addr = Address(addr).to_mask(symbols=7, ellipsis_length=3)
        addr = html_text_colored(addr, TransactionColors().highlight)
        addr = html_text_font(addr, family=TransactionFonts().mono.family())
        return addr

    @classmethod
    def _formatted_domain(cls, domain: str) -> str:
        domain = html_text_colored(domain, TransactionColors().highlight)
        domain += html_text_colored('.ton', TransactionColors().dot_ton)
        domain = html_text_font(domain, weight=TransactionFonts().domain.weight())
        return domain

    @classmethod
    def _formatted_wallet_name(cls, wallet: str) -> str:
        wallet = html_text_colored(wallet, TransactionColors().highlight)
        wallet = html_text_font(wallet, weight=TransactionFonts().domain.weight())
        return wallet

    @property
    def cancellable(self) -> bool:
        return not self.taken

    @property
    def need_dash_animation(self) -> bool:
        return self.kind == TransactionListItemKind.pending


__all__ = ['TransactionListItemData',
           'TransactionListItemKind',
           'TransactionButton']
