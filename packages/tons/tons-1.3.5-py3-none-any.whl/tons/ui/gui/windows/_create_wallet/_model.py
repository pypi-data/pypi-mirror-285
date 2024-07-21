from typing import Union

from PyQt6.QtCore import QObject

from tons.config import Config
from tons.tonclient.utils import KeyStores, BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, \
    RecordNameInvalidError
from tons.tonsdk.contract.wallet import WalletVersionEnum, Wallets
from ..mixins.keystore_selection import KeystoreSelectModel
from ..mixins.wallet_version_selection import WalletVersionSelectModel
from ..mixins.workchain_selection import WorkchainSelectModel


class CreateWalletModel(QObject, KeystoreSelectModel, WalletVersionSelectModel,
                        WorkchainSelectModel):
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
                      comment: str,
                      version: Union[WalletVersionEnum, str],
                      workchain: int):
        keystore = self._keystore
        version = WalletVersionEnum(version)
        mnemonics, _, _, _ = Wallets.create(version, workchain)

        try:
            keystore.add_new_record(wallet_name, mnemonics, version, workchain, comment=comment, save=True)
        except (RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, RecordNameInvalidError):
            raise

__all__ = ["CreateWalletModel", "RecordWithAddressAlreadyExistsError", "RecordWithNameAlreadyExistsError"]
