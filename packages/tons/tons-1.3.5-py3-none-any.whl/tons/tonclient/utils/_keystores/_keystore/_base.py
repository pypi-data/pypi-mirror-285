import contextlib
import dataclasses
import os
from abc import ABC
from base64 import b64encode
from copy import deepcopy
from enum import Enum
from typing import List, Optional, Union, Tuple

from tons.tonclient.utils import RecordDoesNotExistError
from tons.tonclient.utils._exceptions import RecordNameInvalidError, InvalidMnemonicsError, \
    RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, InvalidPrivateKeyError
from tons.tonclient.utils._keystores._record import Record
from ._secret import WalletSecret, get_wallet_from_record_and_secret
from ..._tonconnect import TonconnectConnection, Tonconnector
from tons.tonclient.utils._whitelist import WhitelistContact, LocalWhitelist
from tons.tonclient.utils._multisig import MultiSigWalletRecord, MultiSigOrderRecord, LocalMultiSigWalletList, \
    LocalMultiSigOrderList
from tons.tonsdk.contract.wallet import WalletVersionEnum, Wallets, WalletContract
from tons.tonsdk.crypto.exceptions import InvalidMnemonicsError as sdk_InvalidMnemonicsError
from tons.tonsdk.crypto.exceptions import InvalidPrivateKeyError as sdk_InvalidPrivateKeyError
from tons.tonsdk.utils import Address


class KeyStoreTypeEnum(str, Enum):
    password = "password"
    yubikey = "yubikey"

    def __str__(self):
        return self.value


@dataclasses.dataclass
class KeyStoreUpgradeInfo:
    has_been_upgraded: bool = False
    backup_path: Optional[str] = None
    old_version: Optional[int] = None


class BaseKeyStore(ABC):
    def __init__(self, filepath: str, version: int, keystore_type: KeyStoreTypeEnum,
                 records: Union[List[Record], bytes], contacts: Union[List[WhitelistContact], bytes],
                 connections: Union[List[TonconnectConnection], bytes],
                 multisig_wallets: Union[List[MultiSigWalletRecord], bytes],
                 multisig_orders: Union[List[MultiSigOrderRecord], bytes]):
        self.filepath = filepath
        self.name = os.path.basename(filepath)
        self.type = keystore_type
        self.version = version
        self.crypto = {}
        self._records = records
        self.contacts = contacts
        self.connections = connections
        self.multisig_wallets = multisig_wallets
        self.multisig_orders = multisig_orders

        self._whitelist = None
        self._tonconnector = None
        self._multisig_wallet_list: Optional[LocalMultiSigWalletList] = None
        self._multisig_order_list: Optional[LocalMultiSigOrderList] = None

        self.upgrade_info = KeyStoreUpgradeInfo()

    @property
    def has_been_upgraded(self) -> bool:
        """
        Informs if the keystore has been upgraded to the next version and backed up
        """
        return self.upgrade_info.has_been_upgraded

    def set_upgraded(self, backup_path: str, old_version: int):
        """
        Marks the keystore as upgraded and sets the backup path and old version
        """
        self.upgrade_info.has_been_upgraded = True
        self.upgrade_info.backup_path = backup_path
        self.upgrade_info.old_version = old_version

    def get_records(self, sort_records: bool) -> Tuple[Record,...]:
        if sort_records:
            return tuple(sorted(self._records, key=lambda record: record.name.lower()))
        return tuple(self._records)

    @classmethod
    def new(cls, **kwargs) -> 'BaseKeyStore':
        """
        generate new keystore
        """
        raise NotImplementedError

    @classmethod
    def load(cls, json_data) -> 'BaseKeyStore':
        """
        load keystore from file and upgrade to the latest version if required
        """
        raise NotImplementedError

    def save(self):
        """
        save encoded data to self.filepath file or restore state with records_before in case of an error
        """
        self._save()

    def _save(self):
        raise NotImplementedError

    def unlock(self, **kwargs):
        """
        decode non sensitive records data (e.g. address)
        """
        raise NotImplementedError

    def validate_secret(self, secret):
        """
        validates secret (not locker)
        """
        raise NotImplementedError

    def get_secret(self, record: Record) -> WalletSecret:
        """
        get mnemonics / private key from the record
        """
        raise NotImplementedError

    def _create_record_secret_key(self, mnemonics: List[str]) -> bytes:  # TODO rename
        """
        encode mnemonics
        """
        raise NotImplementedError

    def encrypt_secret(self, secret: bytes) -> bytes:
        """
        encode secret
        """
        raise NotImplementedError

    def decrypt_secret(self, encrypted_secret: bytes) -> bytes:
        """
        decode secret
        """
        raise NotImplementedError

    @property
    def whitelist(self) -> LocalWhitelist:
        """
        local whitelist
        """
        raise NotImplementedError

    @property
    def tonconnector(self) -> Tonconnector:
        """
        tonconnector handles tonconnect connections in a keystore
        """
        raise NotImplementedError

    @property
    def multisig_wallet_list(self) -> LocalMultiSigWalletList:
        raise NotImplementedError

    @property
    def multisig_order_list(self) -> LocalMultiSigOrderList:
        raise NotImplementedError

    def get_record_by_name(self, name: str, raise_none: bool = False) -> Optional[Record]:
        return self._get_record(name=name, raise_none=raise_none)

    def get_record_by_address(self, address: Union[str, Address], raise_none: bool = False) -> Optional[Record]:
        return self._get_record(address=Address(address), raise_none=raise_none)

    def add_new_record_from_pk(self,
                               name: str,
                               private_key: bytes,
                               version: WalletVersionEnum,
                               workchain: int,
                               subwallet_id: Optional[int] = None,
                               comment: Optional[str] = None,
                               save: bool = False,
                               allow_empty_name=False
                               ):
        private_key = private_key[:32]
        sk = self.encrypt_secret(private_key)
        self._validate_record_name(name, allow_empty_name)

        try:
            _, _, wallet = Wallets.from_pk(private_key, version, workchain, subwallet_id)
        except sdk_InvalidPrivateKeyError as exc:
            raise InvalidPrivateKeyError(exc)

        record = Record(name=name, address=wallet.address, version=version, workchain=workchain,
                        subwallet_id=subwallet_id, comment=comment,
                        secret_key=b64encode(sk).decode("utf-8"))
        self._finalize_add_record(record, save)

    def add_new_record(self, name: str,
                       mnemonics: List[str], version: WalletVersionEnum,
                       workchain: int, subwallet_id: Optional[int] = None,
                       comment: Optional[str] = None, save=False, allow_empty_name=False):

        sk = self._create_record_secret_key(mnemonics)
        self._validate_record_name(name, allow_empty_name)

        try:
            _, _, _, wallet = Wallets.from_mnemonics(mnemonics, version, workchain, subwallet_id)
        except sdk_InvalidMnemonicsError as exc:
            raise InvalidMnemonicsError()

        record = Record(name=name, address=wallet.address, version=version, workchain=workchain,
                        subwallet_id=subwallet_id, comment=comment,
                        secret_key=b64encode(sk).decode("utf-8"))

        self._finalize_add_record(record, save)

    def add_new_record_from_secret(self, name: str,
                       secret: WalletSecret, version: WalletVersionEnum,
                       workchain: int, subwallet_id: Optional[int] = None,
                       comment: Optional[str] = None, save=False, allow_empty_name=False):
        if secret.mnemonics:
            self.add_new_record(name,
                                secret.mnemonics.split(),
                                version,
                                workchain,
                                subwallet_id,
                                comment, save=save, allow_empty_name=allow_empty_name)
        else:
            self.add_new_record_from_pk(name,
                                        secret.private_key,
                                        version,
                                        workchain,
                                        subwallet_id,
                                        comment, save=save)

    def get_wallet_from_record(self, record: Record) -> Tuple[WalletContract, WalletSecret]:
        wallet_secret = self.get_secret(record)

        wallet = get_wallet_from_record_and_secret(record, wallet_secret)

        return wallet, wallet_secret

    def _validate_record_name(self, name: str, allow_empty_name: bool):
        if not name and not allow_empty_name:
            raise RecordNameInvalidError('Record name should not be empty.')

    def _finalize_add_record(self, record: Record, save: bool):
        if self.get_record_by_name(record.name) is not None:
            raise RecordWithNameAlreadyExistsError(name=record.name)
        if (existing_record := self.get_record_by_address(record.address)) is not None:
            raise RecordWithAddressAlreadyExistsError(name=existing_record.name,
                                                      address=record.address)
        with self.restore_on_failure():
            self._records.append(record)
            if save:
                self.save()

    def edit_record(self, name: str, new_name: Optional[str], new_comment: Optional[str], save: bool = False):
        record = self.get_record_by_name(name, raise_none=True)
        with self.restore_on_failure():
            record_idx = self._records.index(record)

            if new_name is not None:
                if new_name == '':
                    raise RecordNameInvalidError('Record name should not be empty')

                if name != new_name:
                    if self.get_record_by_name(new_name, raise_none=False) is not None:
                        raise RecordWithNameAlreadyExistsError(name=new_name)

                    self._records[record_idx].name = new_name
                    self.tonconnector.update_wallet_name(name, new_name, save=False)

            if new_comment is not None:
                self._records[record_idx].comment = new_comment

            if save:
                self.save()

    def delete_record(self, name: str, save: bool = False) -> Record:
        record = self.get_record_by_name(name, raise_none=True)
        if save:
            with self.restore_on_failure():
                self.tonconnector.delete_all_by_name(name, save=False)
                self._records.remove(record)
                self.save()
        else:
            self.tonconnector.delete_all_by_name(name, save=False)
            self._records.remove(record)

        return record

    def _get_record(self, name: Optional[str] = None, address: Union[str, Address, None] = None,
                    raise_none: bool = False) -> Optional[Record]:
        record = None

        if name is not None:
            record = next(
                (record for record in self._records if record.name == name), record)
            if record is None and raise_none:
                raise RecordDoesNotExistError(
                    f"Record with the name {name} does not exist")

        if address is not None:
            address = address if isinstance(
                address, str) else address.to_string(False, False, False)
            record = next(
                (record for record in self._records if record.address == address), record)
            if record is None and raise_none:
                raise RecordDoesNotExistError(
                    f"Record with the address {address} does not exist")

        if name is None and address is None and raise_none:
            raise RecordDoesNotExistError("Record with the name/address None does not exist")

        return record

    def pretty_string(self):
        icon = ""
        if self.type == KeyStoreTypeEnum.password:
            icon = "🔒"
        elif self.type == KeyStoreTypeEnum.yubikey:
            icon = "🔐"

        return f"{icon} {os.path.basename(self.filepath)}"

    @property
    def short_name(self):
        return os.path.splitext(self.name)[0]

    @contextlib.contextmanager
    def restore_on_failure(self):
        """
        A context manager that ensures restoration of keystore attributes upon failure.

        This context manager is designed to preserve the state of specific attributes
        of a keystore in case an exception occurs during the execution of the code within
        the context. It deep copies the attributes specified (records, connections, and contacts)
        before the execution of the code block, and restores them to their original state
        if an exception is raised within the block.

        Usage:
        ```python
        with keystore.restore_on_failure():
            # Code block where changes might occur to records, connections, or contacts
            # If an exception occurs here, the state of these attributes will be restored
        ```

        Attributes:
        - self: The object instance that this context manager is applied to.

        Yields:
        None. The context manager is entered and exited automatically.

        Raises:
        Any exception raised within the context block will be re-raised after
        the state restoration.
        """
        records_before = deepcopy(self._records)
        connections_before = deepcopy(self.connections)
        contacts_before = deepcopy(self.contacts)
        try:
            yield
        except Exception as exc:
            self._records = records_before
            self.connections = connections_before

            try:
                self.tonconnector.connections = self.connections
            except NotImplementedError:
                pass

            self.contacts = contacts_before
            try:
                self.whitelist._contacts = self.contacts
            except NotImplementedError:
                pass

            raise exc

