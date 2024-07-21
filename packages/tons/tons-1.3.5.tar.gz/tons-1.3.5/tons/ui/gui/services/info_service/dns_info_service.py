import time
from collections import defaultdict
from typing import Dict, Set, List, Optional, Callable

from PyQt6.QtCore import pyqtSignal, pyqtSlot

from tons.logging_ import tons_logger
from tons.tonclient import TonError
from tons.tonclient._client._base import NftItemInfoResult
from tons.tonsdk.utils import Address
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.utils import slot_exc_handler
from .base_info_service import BaseInfoService


class DnsInfoNotFetched(GuiException):
    pass


class DnsInfoServiceNotSetup(GuiException):
    def __init__(self):
        super().__init__("Address info service not set up: please run address_info_service.setup(ctx) first")


class _DnsInfoService(BaseInfoService):
    UPDATE_INTERVAL_MS = 3000
    FORGET_INTERVAL_SEC = 40  # the address is popped from the monitored address list if not requested regularily

    def __init__(self):
        super().__init__('info service thread')
        self._nft_info_map: Dict[str, Dict[str, NftItemInfoResult]] = defaultdict(dict)
        self._owner_addresses: Set[str] = set()
        self._last_requested: Dict[str, float] = dict()

    def get_list_for_wallet(self, address: str) -> List[NftItemInfoResult]:
        self._place_order(address)
        raw_addr = self._raw(address)
        if raw_addr not in self._nft_info_map:
            raise DnsInfoNotFetched

        return list(self._nft_info_map[raw_addr].values())

    def get_by_wallet_and_domain(self, wallet_address: str, domain: str) -> NftItemInfoResult:
        self._place_order(wallet_address)
        raw_addr = self._raw(wallet_address)
        if raw_addr not in self._nft_info_map or domain not in self._nft_info_map[raw_addr]:
            raise DnsInfoNotFetched

        return self._nft_info_map[self._raw(wallet_address)][domain]

    def clear(self):
        self._nft_info_map = defaultdict(dict)
        self._owner_addresses = set()

    def _place_order(self, address: str):
        raw_address = self._raw(address)
        self._owner_addresses.add(raw_address)
        self._last_requested[raw_address] = time.time()

    def _raw(self, address: str) -> str:
        return Address.raw_id(address)

    def _raw_addresses_to_monitor(self) -> List[str]:
        return [self._raw(addr) for addr in self._owner_addresses.copy()]

    @pyqtSlot()
    @slot_exc_handler()
    def _update(self):
        addresses_to_monitor = self._raw_addresses_to_monitor()
        try:
            self._update_dns_info(addresses_to_monitor)
        except AttributeError:
            raise DnsInfoServiceNotSetup
        except TonError as exception:
            tons_logger().info(f'failed fetch addresses in background ({type(exception).__name__})')
        except CtxReferenceError:
            tons_logger().info(f'failed fetch addresses in background (ctx ref error)')
        else:
            for addr in addresses_to_monitor:
                if addr not in self._nft_info_map:
                    self._nft_info_map[addr] = {}

            self.updated.emit()

        self._clean_old_addresses(addresses_to_monitor)

    def _update_dns_info(self, addresses_to_monitor):
        current_time = int(time.time())
        query = self._ctx.ton_client.form_dns_items_query(addresses_to_monitor, current_time)
        if query is None:
            return

        page = None
        while True:
            page, results = self._ctx.ton_client.get_paginated_dns_items_information(query, page)
            for dns_list_info in results:
                if dns_list_info.owner_or_max_bidder is None or dns_list_info.dns_domain is None:
                    continue

                self._nft_info_map[self._raw(dns_list_info.owner_or_max_bidder)][dns_list_info.dns_domain] = dns_list_info

            if page is None:
                break

            self.updated.emit()

    def _clean_old_addresses(self, addresses_to_monitor: List[str]):
        for raw_address in addresses_to_monitor:
            if self._address_last_requested_long_ago(raw_address):
                self._owner_addresses.remove(raw_address)
                try:
                    del self._nft_info_map[raw_address]
                except KeyError:
                    pass

    def _address_last_requested_long_ago(self, raw_address: str):
        return (time.time() - self._last_requested[raw_address]) > self.FORGET_INTERVAL_SEC


dns_info_service = _DnsInfoService()
