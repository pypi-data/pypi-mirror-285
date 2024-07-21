from typing import Protocol, Union, Optional, Callable

from PyQt6.QtCore import pyqtSlot

from tons.tonclient._client._base import AddressInfoResult
from tons.tonsdk.utils import Address
from ....utils import slot_exc_handler
from ....windows.mixins.wallet_info_service import WalletInfoServicePresenter


class Presenter(Protocol):
    def on_address_info_changed(self): ...


class View(Protocol):
    def setup_list_wallets_signals(self, presenter: Presenter): ...
    def set_address_info(self, get_address_info: Callable[[str], Optional[AddressInfoResult]]): ...


class Model(Protocol):
    def address_info(self, address: Union[Address, str]) -> Optional[AddressInfoResult]: ...


class ListWalletsPresenter(WalletInfoServicePresenter):
    _view: View
    _model: Model

    def init_list_wallets(self):
        self.init_wallet_info_service()

    @pyqtSlot()
    @slot_exc_handler()
    def on_address_info_changed(self):
        self._view.set_address_info(self._model.address_info)


__all__ = ['ListWalletsPresenter']
