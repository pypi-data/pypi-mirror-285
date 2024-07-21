from typing import Optional, Union, List

from PyQt6.QtCore import QObject

from tons.config import Config
from tons.tonclient.utils import KeyStores, BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError
from ..mixins.keystore_selection import KeystoreSelectModel
from ..mixins.wallet_version_selection import WalletVersionSelectModel
from ..mixins.workchain_selection import WorkchainSelectModel


class CreateBatchWalletModel(QObject, KeystoreSelectModel, WalletVersionSelectModel, WorkchainSelectModel):
    def __init__(self,
                 config: Config,
                 keystore: BaseKeyStore,
                 keystores: KeyStores):
        super().__init__()
        self._config = config
        self._keystore = keystore
        self._keystores = keystores

    def set_keystore(self, keystore_name: str):
        self._keystore = self._keystores.get_keystore(keystore_name, raise_none=True)

    def is_in_keystore(self, wallet_name) -> bool:
        record = self._keystore.get_record_by_name(wallet_name, raise_none=False)
        return record is not None


__all__ = ["CreateBatchWalletModel", "RecordWithAddressAlreadyExistsError",
           "RecordWithNameAlreadyExistsError"]

