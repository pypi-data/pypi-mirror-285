import time
from typing import Dict, Set, List

from PyQt6.QtCore import pyqtSignal, pyqtSlot

from tons.logging_ import tons_logger
from tons.tonclient import TonError
from tons.tonclient._client._base import AddressInfoResult
from tons.tonsdk.utils import Address
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.utils import slot_exc_handler
from .base_info_service import BaseInfoService


class AddressInfoNotFetched(GuiException):
    pass


class AddressInfoServiceNotSetup(GuiException):
    def __init__(self):
        super().__init__("Address info service not set up: please run address_info_service.setup(ctx) first")


class _AddressInfoService(BaseInfoService):
    UPDATE_INTERVAL_MS = 1000
    FORGET_INTERVAL_SEC = 3  # the address is popped from the monitored address list if not requested regularily

    updated = pyqtSignal()

    def __init__(self):
        super().__init__('info service thread')
        self._address_info_map: Dict[str, AddressInfoResult] = dict()
        self._addresses: Set[str] = set()
        self._last_requested: Dict[str, float] = dict()

    def get(self, address: str) -> AddressInfoResult:
        self._place_order(address)
        try:
            return self._address_info_map[self._raw(address)]
        except KeyError:
            raise AddressInfoNotFetched

    def clear(self):
        self._address_info_map = dict()
        self._addresses = set()

    def _place_order(self, address: str):
        raw_address = self._raw(address)
        self._addresses.add(raw_address)
        self._last_requested[raw_address] = time.time()

    def _raw(self, address: str) -> str:
        return Address.raw_id(address)

    def _raw_addresses_to_monitor(self) -> List[str]:
        return [self._raw(addr) for addr in self._addresses.copy()]

    @pyqtSlot()
    @slot_exc_handler()
    def _update(self):
        addresses_to_monitor = self._raw_addresses_to_monitor()
        try:
            address_info_results = self._ctx.ton_client.get_addresses_information(addresses_to_monitor)
        except AttributeError as exc:
            raise AddressInfoServiceNotSetup
        except CtxReferenceError:
            tons_logger().info(f'failed fetch addresses in background (ctx ref error)')
        except TonError as exception:
            tons_logger().info(f'failed fetch addresses in background ({type(exception).__name__})')
        else:
            for address, info in zip(addresses_to_monitor, address_info_results):
                self._address_info_map[address] = info

            self.updated.emit()

        self._clean_old_addresses(addresses_to_monitor)

    def _clean_old_addresses(self, addresses_to_monitor: List[str]):
        # TODO this is O(n). Can be optimized through a data struct similar to priority queue
        for raw_address in addresses_to_monitor:
            if self._address_last_requested_long_ago(raw_address):
                self._addresses.remove(raw_address)

    def _address_last_requested_long_ago(self, raw_address: str):
        return (time.time() - self._last_requested[raw_address]) > self.FORGET_INTERVAL_SEC


address_info_service = _AddressInfoService()
