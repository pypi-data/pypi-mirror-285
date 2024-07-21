from typing import Protocol, Optional, Union

from PyQt6.QtCore import pyqtSlot, pyqtSignal

from tons.tonclient._client._base import AddressInfoResult
from tons.tonsdk.utils import Address
from tons.ui.gui.services import address_info_service, AddressInfoNotFetched


class Presenter(Protocol):
    @pyqtSlot()
    def on_address_info_changed(self): ...


class MultiWalletInfoServiceModel:
    _signal_address_info_results_changed = pyqtSignal()

    def setup_wallet_info_signals(self, presenter: Presenter):
        address_info_service.subscribe(presenter.on_address_info_changed)

    def address_info(self, address: Union[Address, str]) -> Optional[AddressInfoResult]:
        try:
            return address_info_service.get(address)
        except AddressInfoNotFetched:
            return None


__all__ = ['MultiWalletInfoServiceModel']
