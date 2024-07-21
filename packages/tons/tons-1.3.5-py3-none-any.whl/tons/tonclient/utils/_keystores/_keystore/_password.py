import json
import os
from base64 import b64decode, b64encode
from hashlib import sha256
from typing import List, Dict

from nacl.bindings import crypto_box_seed_keypair, crypto_box, crypto_box_open

from tons import settings
from tons.tonsdk.contract.wallet import WalletContract
from tons.utils import storage
from ._base import BaseKeyStore, KeyStoreTypeEnum
from ._secret import WalletSecret
from .._crypto import generate_password_keystore, generate_password_keystore_key
from .._record import Record
from ..._multisig import LocalMultiSigWalletList, LocalMultiSigOrderList, MultiSigWalletRecord, MultiSigOrderRecord
from ..._exceptions import KeyStoreInvalidPasswordError, KeyStoreAccessDeniedError, KeyStoreShortPasswordError, \
    KeyStoreWrongPasswordError
from ..._tonconnect import TonconnectConnection, Tonconnector
from ..._whitelist import WhitelistContact, LocalWhitelist


class PasswordKeyStore(BaseKeyStore):

    def __init__(self, filepath, version, records: List[Record], contacts: List[WhitelistContact],
                 connections: List[TonconnectConnection],
                 multisig_wallets: List[MultiSigWalletRecord],
                 multisig_orders: List[MultiSigOrderRecord],
                 public_key, salt):
        super().__init__(filepath, version, KeyStoreTypeEnum.password, records, contacts, connections,
                         multisig_wallets, multisig_orders)

        self.password = None

        self._salt = salt
        self._public_key = public_key

    @classmethod
    def new(cls, filepath: str, password: str) -> 'PasswordKeyStore':
        public_key, salt = generate_password_keystore(password)

        return PasswordKeyStore(
            filepath=filepath,
            version=settings.CURRENT_KEYSTORE_VERSION,
            public_key=public_key,
            salt=salt,
            records=[],
            contacts=[],
            connections=[],
            multisig_wallets=[],
            multisig_orders=[]
        )

    @classmethod
    def load(cls, json_data) -> 'PasswordKeyStore':
        prev_version = json_data["version"]
        if prev_version != settings.CURRENT_KEYSTORE_VERSION:
            json_data = cls.upgrade_from_old_version(prev_version, json_data)

        keystore = PasswordKeyStore(
            filepath=json_data["filepath"],
            version=json_data["version"],
            public_key=b64decode(json_data["crypto"]["public_key"]),
            salt=b64decode(json_data["crypto"]["salt"]),
            records=[Record.parse_obj(record) for record in json_data["records"]],
            contacts=[WhitelistContact.parse_obj(record) for record in json_data["contacts"]],
            connections=[TonconnectConnection.parse_obj(connection) for connection in json_data["connections"]],
            multisig_wallets=[MultiSigWalletRecord.parse_obj(multi_wallet) for multi_wallet in json_data['multisig_wallets']],
            multisig_orders=[MultiSigOrderRecord.parse_obj(multi_order) for multi_order in json_data['multisig_orders']]
        )

        return keystore

    def _save(self):
        records = [record.dict() for record in self._records]
        contacts = [contact.dict() for contact in self.contacts]
        connections = [connection.dict() for connection in self.connections]
        multisig_wallets = [wallet.dict() for wallet in self.multisig_wallets]
        multisig_orders = [order.dict() for order in self.multisig_orders]
        json_data = json.dumps({
            "version": self.version,
            "crypto": {
                "public_key": b64encode(self._public_key).decode('utf-8'),
                "salt": b64encode(self._salt).decode('utf-8'),
                "type": self.type,
            },
            "records": records,
            "contacts": contacts,
            "connections": connections,
            "multisig_wallets": multisig_wallets,
            "multisig_orders": multisig_orders
        }).encode('utf-8')
        hash_of_data = sha256(json_data).digest()
        storage.save_bytes(self.filepath, hash_of_data + json_data)

    def unlock(self):
        # nonsensitive data of the records are already in a readable form
        return

    def validate_secret(self, secret):
        pub_k, priv_k = generate_password_keystore_key(secret, self._salt)
        if pub_k != self._public_key:
            raise KeyStoreWrongPasswordError()

    def get_secret(self, record: Record) -> WalletSecret:
        src = b64decode(record.secret_key)
        decoded_key_bytes = self.decrypt_secret(src)
        wallet_secret = WalletSecret(decoded_key_bytes)
        return wallet_secret

    def _create_record_secret_key(self, mnemonics: List[str]) -> bytes:
        key = (" ".join(mnemonics)).encode('utf-8')
        return self.encrypt_secret(key)

    def encrypt_secret(self, secret: bytes) -> bytes:
        ephemeral_key_public, ephemeral_key_secret = crypto_box_seed_keypair(
            os.urandom(32))
        nonce = os.urandom(24)
        encrypted = crypto_box(secret, nonce, self._public_key, ephemeral_key_secret)

        return nonce + ephemeral_key_public + encrypted

    def decrypt_secret(self, encrypted_secret: bytes) -> bytes:
        if self.password is None:
            raise KeyStoreAccessDeniedError("Password required.")

        nonce, public_key, data = encrypted_secret[:24], encrypted_secret[24:24 + 32], encrypted_secret[24 + 32:]

        pub_k, priv_k = generate_password_keystore_key(self.password, self._salt)
        if pub_k != self._public_key:
            raise KeyStoreWrongPasswordError()

        decoded_key_bytes = crypto_box_open(data, nonce, public_key, priv_k)
        if not decoded_key_bytes:
            raise KeyStoreWrongPasswordError()

        return decoded_key_bytes

    @property
    def whitelist(self) -> LocalWhitelist:
        if self._whitelist is None:
            self._whitelist = LocalWhitelist(self.contacts, self)
        return self._whitelist

    @property
    def tonconnector(self) -> Tonconnector:
        if self._tonconnector is None:
            self._tonconnector = Tonconnector(self.connections, self)
        return self._tonconnector

    @property
    def multisig_wallet_list(self) -> LocalMultiSigWalletList:
        if self._multisig_wallet_list is None:
            self._multisig_wallet_list = LocalMultiSigWalletList(self)
        return self._multisig_wallet_list

    @property
    def multisig_order_list(self) -> LocalMultiSigOrderList:
        if self._multisig_order_list is None:
            self._multisig_order_list = LocalMultiSigOrderList(self)
        return self._multisig_order_list

    @classmethod
    def upgrade_from_old_version(cls, version, json_data) -> Dict:
        if version == 1:
            for record in json_data["records"]:
                record["subwallet_id"] = WalletContract.default_subwallet_id(record["workchain"],
                                                                             record["version"])

            version += 1

        if version == 2:
            json_data["crypto"] = {}
            json_data["crypto"]["public_key"] = b64encode(
                bytes.fromhex(json_data["public_key"])
            ).decode("utf-8")
            json_data["crypto"]["salt"] = b64encode(
                bytes.fromhex(json_data["salt"])
            ).decode("utf-8")

            for record in json_data["records"]:
                record["secret_key"] = b64encode(
                    bytes.fromhex(record["secret_key"])
                ).decode("utf-8")

            json_data["contacts"] = []

            version += 1

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

    @staticmethod
    def validate_password(password: str):
        if len(password) < 6:
            raise KeyStoreShortPasswordError(6)
