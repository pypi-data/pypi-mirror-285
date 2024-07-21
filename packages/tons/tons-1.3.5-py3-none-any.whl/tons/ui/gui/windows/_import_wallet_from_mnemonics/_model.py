from typing import Optional, Union

from PyQt6.QtCore import QObject

from tons.config import Config
from tons.tonclient import TonClient
from tons.tonclient.utils import KeyStores, BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, \
    RecordNameInvalidError, InvalidMnemonicsError
from tons.tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tons.tonsdk.crypto import mnemonic_is_valid
from tons.tonsdk.utils import Address
from ..mixins.keystore_selection import KeystoreSelectModel
from ..mixins.wallet_info_service import SingleWalletInfoServiceModel
from ..mixins.wallet_version_selection import WalletVersionSelectModel
from ..mixins.workchain_selection import WorkchainSelectModel


class ImportWalletFromMnemonicsModel(QObject, SingleWalletInfoServiceModel, KeystoreSelectModel, WalletVersionSelectModel,
                                     WorkchainSelectModel):
    def __init__(self,
                 config: Config,
                 keystore: BaseKeyStore,
                 keystores: KeyStores):
        super().__init__()
        self._config = config  # TODO not needed?
        self._keystore = keystore
        self._keystores = keystores
        self.init_wallet_info_service(None)

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
                      workchain: int,
                      mnemonics: str):
        keystore = self._keystore
        version = WalletVersionEnum(version)
        mnemonics = mnemonics.split()

        try:
            keystore.add_new_record(wallet_name, mnemonics, version, workchain, comment=comment, save=True)
        except (RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, RecordNameInvalidError, InvalidMnemonicsError):
            raise

    @staticmethod
    def can_be_mnemonics(text: str) -> bool:
        mnemonics = text.split()
        return mnemonic_is_valid(mnemonics)

    @staticmethod
    def address_from_mnemonics(mnemonics: str,
                               version,
                               workchain: int,
                               subwallet_id: Optional[int] = None) -> Address:
        mnemonics = mnemonics.split()
        version = WalletVersionEnum(version)
        _, _, _, wallet = Wallets.from_mnemonics(mnemonics, version, workchain, subwallet_id)
        return Address(wallet.address)


__all__ = ["ImportWalletFromMnemonicsModel", "RecordWithAddressAlreadyExistsError", "RecordWithNameAlreadyExistsError"]
