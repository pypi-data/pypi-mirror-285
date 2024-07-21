import webbrowser
from datetime import datetime
from functools import wraps
from typing import Protocol, Union, Optional, Callable, Iterator, List, Tuple, Dict, Sequence

from PyQt6.QtCore import pyqtSlot, pyqtSignal

from tons.config import TonScannerEnum
from tons.logging_ import tons_logger
from tons.tonclient._client._base import NftItemInfoResult
from tons.tonclient.utils import BaseKeyStore
from tons.tonsdk.utils import Address
from tons.ui._utils import dns_expire_soon_threshold, batches, SharedObject
from ..sensitive_area import SensitiveAreaPresenterMixin
from ....exceptions import KeystoreNotUnlocked
from ....utils import slot_exc_handler, DnsRefreshTask, show_message_box_warning, copy_to_clipboard, show_in_scanner
from ....widgets import DnsListItemData
from ....windows.mixins.dns_info_service import DnsInfoServicePresenter


class Presenter(Protocol):
    def on_address_info_changed(self): ...


class View(Protocol):
    def set_dns_info(self, get_dns_info: Callable[[str, str], Optional[NftItemInfoResult]]): ...

    @property
    def selected_dns_model(self) -> Optional[DnsListItemData]: ...

    @property
    def visible_dns_items(self) -> Iterator[DnsListItemData]: ...


class Model(Protocol):
    def dns_info(self, address: Union[Address, str], dns_domain: str) -> Optional[NftItemInfoResult]: ...

    @property
    def keystore(self) -> BaseKeyStore: ...

    def domain_web_page(self, domain: str) -> str: ...

    @property
    def network_is_testnet(self) -> bool: ...

    @property
    def scanner(self) -> TonScannerEnum: ...


def validate_dns_non_skeleton(method):
    @wraps(method)
    def magic(self, *args, **kwargs):
        if self._view.is_skeleton:
            return

        return method(self, *args, **kwargs)
    return magic


class ListDnsPresenter(DnsInfoServicePresenter, SensitiveAreaPresenterMixin):
    _view: View
    _model: Model

    _dns_refresh_intent = pyqtSignal(list)

    def init_list_dns(self):
        self.init_dns_info_service()

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_copy_domain(self):
        copy_to_clipboard(self._view.selected_dns_model.domain)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_show_dns_in_scanner(self):
        webbrowser.open(self._model.domain_web_page(self._view.selected_dns_model.domain))

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_show_dns_contract_in_scanner(self):
        show_in_scanner(self._view.selected_dns_model.dns_account_address,
                        self._model.network_is_testnet,
                        self._model.scanner)

    @pyqtSlot()
    @slot_exc_handler()
    def on_dns_info_changed(self):
        self._view.set_dns_info(self._model.dns_info)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_copy_dns_contract_address(self):
        copy_to_clipboard(self._view.selected_dns_model.dns_account_address)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_copy_owner_or_max_bidder_address(self):
        copy_to_clipboard(self._view.selected_dns_model.wallet_address)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_dns_refresh_selected_list_item(self):
        items_to_refresh = tuple([self._view.selected_dns_model])
        self._refresh_dns(items_to_refresh)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_action_dns_refresh_all(self):
        items_to_refresh = tuple(self._view.visible_dns_items)
        self._refresh_dns(items_to_refresh)

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_action_dns_refresh_expiring_in(self):
        items_to_refresh = tuple(item for item in self._view.visible_dns_items if self._expires_soon(item.dns_expires))
        self._refresh_dns(items_to_refresh)

    def _refresh_dns(self, dns_list_items: Sequence[DnsListItemData]):
        if len(dns_list_items) == 0:
            show_message_box_warning("No DNS to refresh",
                                     f"There are no DNS items to refresh for the specified filter")
            return

        keystore = self._model.keystore
        message = f'Enter keystore password'
        if len(dns_list_items) == 0:
            title = f'Refresh {dns_list_items[0].domain}.ton domain'
        else:
            title = f'Refresh {len(dns_list_items)} domains'

        try:
            with self.keystore_sensitive(keystore, message, title):
                tasks = self._get_dns_refresh_tasks(dns_list_items, keystore)
        except KeystoreNotUnlocked:
            return

        self._dns_refresh_intent.emit(tasks)

    @classmethod
    def _get_dns_refresh_tasks(cls, dns_list_items: Sequence[DnsListItemData], keystore: BaseKeyStore) \
            -> List[DnsRefreshTask]:
        tasks = []
        for sender_address, sender_dns_list_items in cls._dns_list_items_grouped_by_sender(dns_list_items).items():
            sender = keystore.get_record_by_address(address=sender_address)
            secret = keystore.get_secret(sender)

            for dns_list_item_batch in cls._dns_list_item_batches(sender_dns_list_items):
                dns_items = [dns_list_item.nft_info for dns_list_item in dns_list_item_batch]
                assert all(dns_items)
                tasks.append(
                    DnsRefreshTask(secret=secret, sender=sender, dns_items=dns_items)
                )
        return tasks

    @classmethod
    def _dns_list_item_batches(cls, sender_dns_list_items: Sequence[DnsListItemData],
                                    batch_size: int = 4) -> Iterator[Sequence[DnsListItemData]]:
        yield from batches(sender_dns_list_items, batch_size)


    @classmethod
    def _dns_list_items_grouped_by_sender(cls, dns_list_items: Sequence[DnsListItemData]) \
            -> Dict[str, List[DnsListItemData]]:
        matrix: Dict[str, List[DnsListItemData]] = dict()
        for dns_list_item in dns_list_items:
            addr = dns_list_item.wallet_address
            if not addr in matrix:
                matrix[addr] = []

            matrix[addr].append(dns_list_item)

        return matrix

    def _expires_soon(self, dns_expires: int):
        return datetime.utcfromtimestamp(dns_expires) \
               < dns_expire_soon_threshold(self._model.ctx.config.dns.max_expiring_in)  # TODO refactor: make model property


__all__ = ['ListDnsPresenter', 'validate_dns_non_skeleton']
