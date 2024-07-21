from typing import Protocol, Optional, Union, List

from PyQt6.QtCore import pyqtSlot, pyqtSignal

from tons.tonclient._client._base import NftItemInfoResult
from tons.tonsdk.utils import Address
from tons.ui.gui.services import dns_info_service
from tons.ui.gui.services.info_service.dns_info_service import DnsInfoNotFetched


class Presenter(Protocol):
    @pyqtSlot()
    def on_dns_info_changed(self): ...


class MultiDnsInfoServiceModel:
    _signal_address_info_results_changed = pyqtSignal()

    def setup_dns_info_signals(self, presenter: Presenter):
        dns_info_service.subscribe(presenter.on_dns_info_changed)

    def dns_records(self, address: Union[Address, str]) -> Optional[List[NftItemInfoResult]]:
        try:
            return dns_info_service.get_list_for_wallet(address)
        except DnsInfoNotFetched:
            return None

    def dns_info(self, address: Union[Address, str], dns_domain: str) -> Optional[NftItemInfoResult]:
        try:
            return dns_info_service.get_by_wallet_and_domain(address, dns_domain)
        except DnsInfoNotFetched:
            return None


__all__ = ['MultiDnsInfoServiceModel']
