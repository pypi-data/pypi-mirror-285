from typing import Optional, Union

from PyQt6.QtCore import QObject
from pydantic import BaseModel, root_validator

from tons.config import Config
from tons.tonclient.utils import KeyStores, BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, \
    RecordNameInvalidError
from tons.tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tons.tonsdk.crypto.exceptions import InvalidPrivateKeyError
from tons.tonsdk.utils import Address
from ..mixins.keystore_selection import KeystoreSelectModel
from ..mixins.wallet_info_service import SingleWalletInfoServiceModel
from ..mixins.wallet_version_selection import WalletVersionSelectModel
from ..mixins.workchain_selection import WorkchainSelectModel
from ...exceptions import GuiException


def _address_from_private_key(private_key: bytes,
                              version: Union[str, WalletVersionEnum],
                              workchain: int,
                              subwallet_id: Optional[int] = None) -> Address:
    version = WalletVersionEnum(version)
    try:
        _, _, wallet = Wallets.from_pk(private_key, version, workchain, subwallet_id)
    except InvalidPrivateKeyError as exc:
        raise exc
    return Address(wallet.address)


class PrivateKeyNotSelected(GuiException):
    pass


class _WalletModel(BaseModel):
    version: WalletVersionEnum
    workchain: int
    subwallet_id: Optional[int] = None
    private_key: Optional[bytes] = None
    _address: Optional[Address] = None

    class Config:
        validate_assignment = True

    @root_validator
    def _update_address(cls, values):
        if values.get('private_key') is None:
            values['_address'] = None
            return values

        values['_address'] = _address_from_private_key(
            values['private_key'],
            values['version'],
            values['workchain'],
            values['subwallet_id']
        )
        return values

    def address(self) -> Optional[Address]:
        return self._address



class ImportWalletFromPrivateKeyModel(QObject, SingleWalletInfoServiceModel, KeystoreSelectModel, WalletVersionSelectModel,
                                     WorkchainSelectModel):
    def __init__(self,
                 config: Config,
                 keystore: BaseKeyStore,
                 keystores: KeyStores):
        super().__init__()
        self._config = config
        self._keystore = keystore
        self._keystores = keystores
        self.init_wallet_info_service(None)

        self._wallet_model = _WalletModel(version = self.default_wallet_version,
                                          workchain = self.default_workchain)

    def set_keystore(self, keystore_name: str):
        self._keystore = self._keystores.get_keystore(keystore_name, raise_none=True)

    def is_in_keystore(self, wallet_name) -> bool:
        record = self._keystore.get_record_by_name(wallet_name, raise_none=False)
        return record is not None

    @property
    def default_wallet_name(self):
        new_wallet_pattern = "New wallet %03d"
        idx = 1
        new_wallet_name = new_wallet_pattern % idx
        while self.is_in_keystore(new_wallet_name):
            idx += 1
            new_wallet_name = new_wallet_pattern % idx
        return new_wallet_name

    def create_wallet(self,
                      wallet_name: str,
                      comment: str):
        keystore = self._keystore
        version = self._wallet_model.version
        private_key = self._wallet_model.private_key
        workchain = self._wallet_model.workchain

        if not private_key:
            raise PrivateKeyNotSelected

        try:
            keystore.add_new_record_from_pk(wallet_name, private_key, version, workchain, comment=comment, save=True)
        except (RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, RecordNameInvalidError, InvalidPrivateKeyError):
            raise

    def set_private_key_path(self, file_path: str):
        """
        :raises: InvalidPrivateKeyError, OSError
        """
        with open(file_path, 'rb') as f:
            private_key = f.read()

        self._wallet_model.private_key = private_key
        self._address = self._wallet_model.address()

    def set_wallet_model_info(self, version: Union[str, WalletVersionEnum], workchain: int):
        self._wallet_model.version = WalletVersionEnum(version)
        self._wallet_model.workchain = workchain
        self._address = self._wallet_model.address()



__all__ = ["ImportWalletFromPrivateKeyModel", "RecordWithAddressAlreadyExistsError", "RecordWithNameAlreadyExistsError"]
