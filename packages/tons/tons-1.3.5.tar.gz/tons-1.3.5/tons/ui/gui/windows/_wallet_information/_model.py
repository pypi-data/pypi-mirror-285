from copy import deepcopy
from typing import Optional

from PyQt6.QtCore import QObject

from tons.tonclient._client._base import AddressInfoResult, TonClient
from tons.tonclient.utils import Record, BaseKeyStore, RecordAlreadyExistsError, RecordNameInvalidError, KeyStores, \
    KeyStoreTypeEnum, InvalidMnemonicsError, WalletSecret
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError
from ..mixins.keystore_selection import KeystoreSelectModel
from ..mixins.wallet_info_service import SingleWalletInfoServiceModel
from ...exceptions import GuiException


class MnemonicsNotPresent(GuiException):
    def __init__(self):
        super().__init__("Mnemonics are not present for this wallet.")


class WalletInformationModel(QObject, SingleWalletInfoServiceModel, KeystoreSelectModel):
    def __init__(self,
                 keystores: KeyStores,
                 keystore: BaseKeyStore,
                 record: Record):

        super().__init__()
        if keystore.type == KeyStoreTypeEnum.yubikey:
            raise NotImplementedError("Yubikey is not yet supported in GUI")

        self._keystore: BaseKeyStore = keystore
        self._keystores: KeyStores = keystores

        self._record: Record = deepcopy(record)

        self.init_wallet_info_service(record.address)

    def _load_record(self, name: str):
        self._record = deepcopy(self._keystore.get_record_by_name(name))

    def save(self,
             wallet_name: str,
             comment: str,
             keystore_dst_name: Optional[str] = None):
        if keystore_dst_name is None:
            self._edit_wallet(wallet_name, comment)
        else:
            self._move_wallet(wallet_name, comment, keystore_dst_name)
        self._load_record(wallet_name)

    def _edit_wallet(self, wallet_name: str, comment: str):
        try:
            self._keystore.edit_record(self._record.name, wallet_name, comment, save=True)
        except (RecordAlreadyExistsError, RecordNameInvalidError):
            raise

    def _move_wallet(self,
                     new_name: str,
                     new_comment: str,
                     new_keystore_name: str):
        keystore_dst = self._get_keystore(new_keystore_name)
        secret = self.get_secret()
        try:
            keystore_dst.add_new_record_from_secret(new_name,
                                                    secret,
                                                    self._record.version,
                                                    self._record.workchain,
                                                    self._record.subwallet_id,
                                                    new_comment,
                                                    save=True)
        except (RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, RecordNameInvalidError):
            raise
        except InvalidMnemonicsError:
            assert False, "Mnemonics are loaded from keystore and thus should not be incorrect"

        self._keystore.delete_record(self._record.name, save=True)
        self._keystore = keystore_dst

    def _get_keystore(self, keystore_name: str) -> BaseKeyStore:
        return self._keystores.get_keystore(keystore_name, raise_none=True)

    def get_mnemonics(self) -> str:
        secret = self._keystore.get_secret(self._record)
        if not secret.mnemonics:
            raise MnemonicsNotPresent
        return secret.mnemonics

    def get_secret(self) -> WalletSecret:
        return self._keystore.get_secret(self._record)

    @property
    def keystore(self) -> BaseKeyStore:
        return self._keystore

    @property
    def record(self) -> Record:
        return self._record


__all__ = ['WalletInformationModel',
           'RecordNameInvalidError',
           'RecordAlreadyExistsError',
           'RecordWithNameAlreadyExistsError',
           'RecordWithAddressAlreadyExistsError',
           'MnemonicsNotPresent']