import json
from base64 import b64encode, b64decode
from hashlib import sha256
from typing import List, Union, Optional, Dict

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from ykman import scripting as s
from yubikit.piv import PivSession, SLOT as PIV_SLOT, KEY_TYPE

from tons import settings
from tons.utils import storage
from ._base import BaseKeyStore, KeyStoreTypeEnum
from ._secret import WalletSecret
from .._crypto import AESCipher, generate_yubikey_keystore
from .._record import Record
from ... import KeyStoreAccessDeniedError
from ..._multisig import LocalMultiSigWalletList, LocalMultiSigOrderList, MultiSigWalletRecord, MultiSigOrderRecord
from ..._tonconnect import TonconnectConnection, Tonconnector
from ..._whitelist import WhitelistContact, LocalWhitelist


class YubikeyKeyStore(BaseKeyStore):
    SLOT = PIV_SLOT.RETIRED6
    KEY_TYPE = KEY_TYPE.RSA2048
    HASH_ALGO = hashes.SHA256()
    PADDING = PKCS1v15()

    def __init__(self, filepath, version,
                 records: Union[List[Record], bytes], contacts: Union[List[WhitelistContact], bytes],
                 connections: Union[List[TonconnectConnection], bytes],
                 multisig_wallets: Union[List[MultiSigWalletRecord], bytes],
                 multisig_orders: Union[List[MultiSigOrderRecord], bytes],
                 piv_session: Optional[PivSession], iv: bytes, encrypted_key: bytes,
                 slot=None, key_type=None, hash_algo=None, padding=None):
        super().__init__(filepath, version, KeyStoreTypeEnum.yubikey, records, contacts, connections,
                         multisig_wallets, multisig_orders)

        self.piv_session = piv_session
        self.locked = records is not List

        self._iv = iv
        self._encrypted_key = encrypted_key
        self._slot = slot or self.SLOT
        self._key_type = key_type or self.KEY_TYPE
        self._hash_algo = hash_algo or self.HASH_ALGO
        self._padding = padding or self.PADDING

    @classmethod
    def new(cls, filepath: str, pin: str) -> 'YubikeyKeyStore':
        key, iv = generate_yubikey_keystore()

        # fixme: bad for GUI
        piv_session = PivSession(s.single().smart_card())
        piv_session.verify_pin(pin)

        encrypted_key = piv_session.attest_key(cls.SLOT).public_key().encrypt(
            key,
            padding=cls.PADDING
        )

        return YubikeyKeyStore(
            filepath=filepath,
            version=settings.CURRENT_KEYSTORE_VERSION,
            records=[],
            contacts=[],
            connections=[],
            multisig_wallets=[],
            multisig_orders=[],
            piv_session=piv_session,
            iv=iv,
            encrypted_key=encrypted_key,
            slot=cls.SLOT,
            padding=cls.PADDING
        )

    @classmethod
    def load(cls, json_data) -> 'YubikeyKeyStore':
        prev_version = json_data["version"]
        if prev_version != settings.CURRENT_KEYSTORE_VERSION:
            json_data = cls.upgrade_from_old_version(prev_version, json_data)

        return YubikeyKeyStore(
            filepath=json_data["filepath"],
            version=json_data["version"],
            records=json_data["records"],
            contacts=json_data["contacts"],
            connections=json_data["connections"],
            multisig_wallets=[MultiSigWalletRecord.parse_obj(multi_wallet) for multi_wallet in
                              json_data['multisig_wallets']],
            multisig_orders=[MultiSigOrderRecord.parse_obj(multi_order) for multi_order in json_data['multisig_orders']],
            piv_session=None,
            iv=b64decode(json_data["crypto"]["iv"]),
            encrypted_key=b64decode(json_data["crypto"]["cipher_text"])
        )

    def _save(self):
        records_str = json.dumps([record.dict() for record in self._records])
        contacts_str = json.dumps([contact.dict() for contact in self.contacts])
        connections_str = json.dumps([connection.dict() for connection in self.connections])
        key = self.piv_session.decrypt(self._slot, self._encrypted_key, self._padding)
        records_encoded = AESCipher(key, self._iv).encrypt(records_str)
        contacts_encoded = AESCipher(key, self._iv).encrypt(contacts_str)
        connections_encoded = AESCipher(key, self._iv).encrypt(connections_str)
        json_data = json.dumps({
            "version": self.version,
            "crypto": {
                "cipher_text": b64encode(self._encrypted_key).decode('utf-8'),
                "iv": b64encode(self._iv).decode("utf-8"),
                "slot": self._slot,
                "type": self.type,
            },
            "records": records_encoded,
            "contacts": contacts_encoded,
            "connections": connections_encoded,
        }).encode('utf-8')
        hash_of_data = sha256(json_data).digest()
        storage.save_bytes(self.filepath, hash_of_data + json_data)

    def unlock(self, pin: str):
        if self.locked:
            piv_session = PivSession(s.single().smart_card())
            piv_session.verify_pin(pin)
            self.piv_session = piv_session
            key = self.piv_session.decrypt(self._slot, self._encrypted_key, self._padding)
            records = json.loads(AESCipher(key, self._iv).decrypt(self._records))
            contacts = json.loads(AESCipher(key, self._iv).decrypt(self.contacts))
            connections = json.loads(AESCipher(key, self._iv).decrypt(self.connections))
            self._records = [Record.parse_obj(record) for record in records]
            self.contacts = [WhitelistContact.parse_obj(contact) for contact in contacts]
            self.connections = [TonconnectConnection.parse_obj(connection) for connection in connections]
            self.locked = False

    def validate_secret(self, secret):
        pass

    def get_secret(self, record: Record) -> WalletSecret:
        if self.locked:
            raise KeyStoreAccessDeniedError("Unlock the keystore first.")

        src = b64decode(record.secret_key)
        decoded_key_bytes = self.piv_session.decrypt(self._slot, src, self._padding)
        wallet_secret = WalletSecret(decoded_key_bytes)
        return wallet_secret

    def _create_record_secret_key(self, mnemonics: List[str]):
        secret_key = (" ".join(mnemonics)).encode('utf-8')
        return self.piv_session.attest_key(self._slot).public_key().encrypt(
            secret_key,
            padding=self._padding,
        )

    def encrypt_secret(self, secret: bytes) -> bytes:
        return self.piv_session.attest_key(self._slot).public_key().encrypt(
            secret, padding=self._padding, )

    def decrypt_secret(self, encrypted_secret: bytes) -> bytes:
        return self.piv_session.decrypt(self._slot, encrypted_secret, self._padding)

    @property
    def whitelist(self) -> LocalWhitelist:
        if self.locked:
            raise KeyStoreAccessDeniedError("Unlock the keystore first.")
        if self._whitelist is None:
            self._whitelist = LocalWhitelist(self.contacts, self)
        return self._whitelist

    @property
    def tonconnector(self) -> Tonconnector:
        if self.locked:
            raise KeyStoreAccessDeniedError("Unlock the keystore first.")
        if self._tonconnector is None:
            self._tonconnector = Tonconnector(self.connections, self)
        return self._tonconnector

    @property
    def multisig_wallet_list(self) -> LocalMultiSigWalletList:
        if self.locked:
            raise KeyStoreAccessDeniedError("Unlock the keystore first.")
        if self._multisig_wallet_list is None:
            self._multisig_wallet_list = LocalMultiSigWalletList(self)
        return self._multisig_wallet_list

    @property
    def multisig_order_list(self) -> LocalMultiSigOrderList:
        if self.locked:
            raise KeyStoreAccessDeniedError("Unlock the keystore first.")
        if self._multisig_order_list is None:
            self._multisig_order_list = LocalMultiSigOrderList(self)
        return self._multisig_order_list

    # TODO MULTISIG

    @classmethod
    def upgrade_from_old_version(cls, version, json_data) -> Dict:
        if version == 3:
            if "contacts" not in json_data:
                json_data["contacts"] = []
            version += 1

        if version == 4:
            if "connections" not in json_data:
                json_data["connections"] = []
            version += 1

        if version == 5:
            if "multisig_wallets" not in json_data:
                json_data["multisig_wallets"] = []
            if "multisig_orders" not in json_data:
                json_data["multisig_orders"] = []
            version += 1

        json_data["version"] = version
        return json_data
