import weakref
from typing import Optional

from PyQt6.QtCore import QObject

from tons.tonclient.utils import BaseKeyStore, Record, WhitelistContact
from tons.tonsdk.boc import Cell
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.widgets import WalletListItemData
from tons.ui.gui.windows.mixins.wallet_info_service import MultiWalletInfoServiceModel


class InvalidBocFileError(Exception):
    def __init__(self, message):
        self.message = message


class TransferModel(QObject, MultiWalletInfoServiceModel):

    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore):
        super().__init__()
        self.__ctx = weakref.ref(ctx)
        self._keystore = keystore

        self._wallet_from: Optional[WalletListItemData] = None
        self._wallet_to: Optional[WalletListItemData] = None

    @property
    def ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    @property
    def keystore_name(self) -> str:
        return self._keystore.short_name

    @property
    def keystore(self) -> BaseKeyStore:
        return self._keystore

    @property
    def record(self) -> Record:
        if self.wallet_from is None:
            raise RecordNotSelected

        record = self.wallet_from.entity
        assert isinstance(record, Record)
        return record

    @property
    def recipient(self) -> WhitelistContact:
        if self.wallet_to is None:
            raise ContactNotSelected

        entity = self.wallet_to.entity
        if isinstance(entity, WhitelistContact):
            return entity

        assert isinstance(entity, Record)
        return WhitelistContact(name=entity.name, address=entity.address_to_show)

    @property
    def wallet_from(self) -> Optional[WalletListItemData]:
        return self._wallet_from

    @property
    def wallet_to(self) -> Optional[WalletListItemData]:
        return self._wallet_to

    @wallet_from.setter
    def wallet_from(self, wallet: WalletListItemData):
        self._wallet_from = wallet

    @wallet_to.setter
    def wallet_to(self, wallet: WalletListItemData):
        self._wallet_to = wallet

    @property
    def _address_from(self) -> Optional[str]:
        try:
            return self._wallet_from.address
        except AttributeError:
            return

    @property
    def _address_to(self) -> Optional[str]:
        try:
            return self._wallet_to.address
        except AttributeError:
            return

    def update_wallet_models_with_address_info(self):
        if self._wallet_from is not None:
            address_info = self.address_info(self._wallet_from.address)
            self._wallet_from.set_address_info(address_info)

        if self._wallet_to is not None:
            address_info = self.address_info(self._wallet_to.address)
            self._wallet_to.set_address_info(address_info)

    @staticmethod
    def parse_boc(path: Optional[str]) -> Optional[Cell]:
        if not path:
            return None

        try:
            with open(path, 'rb') as file_obj:
                boc = file_obj.read()
        except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
            raise InvalidBocFileError(message=f"Failed to open file: '{path}'")
        try:
            return Cell.one_from_boc(boc)
        except Exception:
            raise InvalidBocFileError(message="Failed to parse bag of cells")

    def _get_keystore(self) -> BaseKeyStore:
        keystore_name = self.keystore_name
        keystore = self.ctx.keystores.get_keystore(keystore_name, raise_none=True)
        return keystore


class RecordNotSelected(GuiException):
    def __init__(self):
        super().__init__('Keystore record not selected')


class ContactNotSelected(GuiException):
    def __init__(self):
        super().__init__('Recipient not selected')
