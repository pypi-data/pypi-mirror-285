from decimal import Decimal
from typing import Protocol, Optional, Union

from PyQt6.QtCore import pyqtSlot

from tons.tonclient._client._base import AddressInfoResult
from tons.tonsdk.utils import Address
from tons.ui.gui.services import address_info_service, AddressInfoNotFetched
from tons.ui.gui.exceptions import GuiException
from tons.ui.gui.services import ton_usd_price
from tons.ui.gui.utils import xstr


class Presenter(Protocol):
    @pyqtSlot()
    def on_address_info_changed(self): ...


class SingleWalletInfoServiceModelNotInitialized(GuiException):
    def __init__(self):
        super().__init__("Please run SingleWalletInfoServiceModel.init_wallet_info_service(address)")


class SingleWalletInfoServiceModel:
    _address: Optional[Address]

    def init_wallet_info_service(self, address: Optional[Address] = None):
        self._address = address

    def setup_wallet_info_signals(self, presenter: Presenter):
        address_info_service.subscribe(presenter.on_address_info_changed)

    @property
    def address(self) -> Optional[Address]:
        return self._address

    @address.setter
    def address(self, value: Optional[Union[Address, str]]):
        if value is None:
            self._address = None
        else:
            self._address = Address(value)

    @property
    def address_code(self) -> str:
        try:
            code = self.address_info.code
        except AttributeError:
            code = None
        return xstr(code)

    @property
    def address_data(self) -> str:
        try:
            data = self.address_info.data
        except AttributeError:
            data = None
        return xstr(data)

    @property
    def address_info(self) -> Optional[AddressInfoResult]:
        try:
            if self._address is None:
                return None
            return address_info_service.get(self._address)
        except AddressInfoNotFetched:
            return None
        except AttributeError:
            raise SingleWalletInfoServiceModelNotInitialized

    @property
    def ton_fiat_price(self) -> Optional[Decimal]:
        return ton_usd_price()

    @property
    def fiat_symbol(self):
        return "$"

    @property
    def balance_fiat(self) -> Optional[Decimal]:
        if (self.ton_fiat_price is None) or (self.address_info.balance is None):
            """ Unknown fiat price """
            return None
        return self.address_info.balance * self.ton_fiat_price


__all__ = ['SingleWalletInfoServiceModel']
