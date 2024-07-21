import weakref
from enum import Enum
from typing import Optional, Union, List, Tuple

from PyQt6.QtCore import QObject

from tons.tonclient._client._base import AddressInfoResult
from tons.tonclient.utils import WhitelistContact
from tons.tonsdk.utils import Address, InvalidAddressError
from tons.ui._utils import SharedObject
from ..components.whitelists import WhitelistsModelComponent
from ..mixins.wallet_info_service import SingleWalletInfoServiceModel
from ...exceptions import CtxReferenceError
from ...utils import ContactLocation


class AddressTypeEnum(int, Enum):
    bounceable = 1
    nonbounceable = 2
    raw = 3

    @classmethod
    def detect(cls, address: Union[str, Address]) -> 'AddressTypeEnum':
        address = Address(address)
        if not address.is_user_friendly:
            return cls.raw
        elif not address.is_bounceable:
            return cls.nonbounceable
        else:
            return cls.bounceable


class ContactInformationModel(QObject, SingleWalletInfoServiceModel):
    def __init__(self,
                 ctx: SharedObject,
                 contact: WhitelistContact,
                 contact_location: ContactLocation):

        super().__init__()
        self._contact = contact
        self._location = contact_location
        self.__ctx = weakref.ref(ctx)
        self.whitelists = WhitelistsModelComponent(ctx)
        self.init_wallet_info_service(Address(contact.address))

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    @staticmethod
    def morph_additional_address_types(address: Union[str, Address]) -> List[Tuple[AddressTypeEnum, str]]:
        address = Address(address)
        address_type = AddressTypeEnum.detect(address)
        remaining_types = set(AddressTypeEnum) - {address_type}
        remaining_types = sorted(remaining_types)

        result = []
        for address_type in remaining_types:
            additional_address = ContactInformationModel._convert_to_address_type(address, address_type)
            result_item = address_type, additional_address
            result.append(result_item)

        return result

    @staticmethod
    def _convert_to_address_type(address: Union[str, Address], address_type: AddressTypeEnum) -> str:
        if address_type == AddressTypeEnum.raw:
            additional_address = Address(address).to_string(False, False, False)
        elif address_type == AddressTypeEnum.nonbounceable:
            additional_address = Address(address).to_string(True, True, False)
        elif address_type == AddressTypeEnum.bounceable:
            additional_address = Address(address).to_string(True, True, True)
        else:
            raise NotImplementedError("Unknown address type")

        return additional_address

    def edit_contact(self, new_name: str, new_address: str, new_default_message: str):
        whitelist = self.whitelists.get_whitelist(self._location)
        whitelist.edit_contact(self._contact.name, new_name, new_address, new_default_message, save=True)

    def move_contact(self, new_name: str, new_address: str, new_default_message: str, new_location: ContactLocation):
        whitelist_dst = self.whitelists.get_whitelist(new_location)
        whitelist_dst.add_contact(new_name, new_address, new_default_message, save=True)
        whitelist_src = self.whitelists.get_whitelist(self._location)
        whitelist_src.delete_contact(self._contact, save=True)

    @property
    def contact(self) -> WhitelistContact:
        return self._contact

    @property
    def location(self) -> ContactLocation:
        return self._location

    @staticmethod
    def address_invalid(address: str) -> bool:
        try:
            Address(address)
        except InvalidAddressError:
            return True
        else:
            return False


__all__ = ['ContactInformationModel', 'AddressTypeEnum']