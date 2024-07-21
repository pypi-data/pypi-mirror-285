from typing import Tuple, Union

from PyQt6.QtCore import QObject
from pydantic import ValidationError

from tons.config import TonNetworkEnum, TonScannerEnum
from tons.tonclient.utils import WhitelistContactAlreadyExistsError, WhitelistContactNameInvalidError, BaseWhitelist, \
    WhitelistContactDoesNotExistError
from tons.tonsdk.utils import InvalidAddressError, Address
from tons.ui._utils import SharedObject
from tons.ui.gui.utils import ContactLocation
from tons.ui.gui.windows.components.whitelists import WhitelistsModelComponent
from tons.ui.gui.windows.mixins.wallet_info_service import SingleWalletInfoServiceModel


class CreateContactModel(QObject, SingleWalletInfoServiceModel):
    def __init__(self, ctx: SharedObject):
        super().__init__()
        self._config = ctx.config
        self.whitelists = WhitelistsModelComponent(ctx)
        self.init_wallet_info_service(None)

    def get_default_contact_name(self, location: ContactLocation):
        whitelist = self.whitelists.get_whitelist(location)
        new_contact_pattern = "New contact %03d"
        idx = 1
        new_contact_name = new_contact_pattern % idx
        while self.is_in_whitelist(new_contact_name, whitelist):
            idx += 1
            new_contact_name = new_contact_pattern % idx
        return new_contact_name

    @staticmethod
    def is_in_whitelist(contact_name: str, whitelist: BaseWhitelist):
        try:
            whitelist.get_contact(contact_name, raise_none=True)
        except WhitelistContactDoesNotExistError:
            return False
        else:
            return True

    @staticmethod
    def address_is_valid(maybe_address: str) -> bool:
        try:
            Address(maybe_address)
        except InvalidAddressError:
            return False
        else:
            return True

    @property
    def network_is_testnet(self) -> bool:  # TODO: DRY: make a ShowInScannerMixin
        return self._config.provider.dapp.network == TonNetworkEnum.testnet

    @property
    def scanner(self) -> TonScannerEnum:
        return self._config.gui.scanner

    def create_contact(self, location: ContactLocation, name: str,
                       address: str, default_message: str):
        whitelist = self.whitelists.get_whitelist(location)
        try:
            whitelist.add_contact(name, address, default_message, save=True)
        except (InvalidAddressError, WhitelistContactAlreadyExistsError,
                WhitelistContactNameInvalidError, ValidationError):
            raise
