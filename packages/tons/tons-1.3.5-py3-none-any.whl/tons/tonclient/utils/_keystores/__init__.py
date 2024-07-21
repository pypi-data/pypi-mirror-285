import json
import os
import shutil
import time
from hashlib import sha256
from typing import Optional, Tuple, List

from tons import settings
from tons.utils import storage
from ._backup import KeystoreBackup, RecordBackup, TonCliRecordBackup
from ._keystore import YubikeyKeyStore, KeyStoreTypeEnum, PasswordKeyStore, BaseKeyStore
from ._record import Record
from .._exceptions import KeyStoreAlreadyExistsError, \
    KeyStoreDoesNotExistError, InvalidKeyStoreError, \
    KeyStoreIsNotSpecifiedError, KeyStoreNameInvalidError


class KeyStores:
    def __init__(self, keystores_workdir: str):
        self.keystores_workdir = keystores_workdir

        paths = storage.get_filenames_by_ptrn(
            keystores_workdir, "*" + settings.KEYSTORE_FILE_EXT)
        self.keystore_paths = {os.path.basename(path): path for path in paths}
        self._keystore_path = None

    def keystore_already_exists(self, name: str) -> bool:
        """
        Check whether a keystore with the given name already exists. Case-insensitive.

        Args:
            name (str): The name of the keystore, with or without the file extension.

        Returns:
            bool: True if a keystore with the given name exists, False otherwise.
        """
        name_to_compare = self.__keystore_name(name).lower()
        keystore_names_lower = [name.lower() for name in self.keystore_paths]
        return name_to_compare in keystore_names_lower

    def create_new_keystore(self, name: str, keystore_type: KeyStoreTypeEnum,
                            secret: Optional[str] = None,
                            save: bool = False) -> BaseKeyStore:
        if not name or name == settings.KEYSTORE_FILE_EXT:
            raise KeyStoreNameInvalidError("Keystore name should not be empty")

        if self.keystore_already_exists(name):
            raise KeyStoreAlreadyExistsError(f"Keystore with the name '{name}' already exists")

        name = self.__keystore_name(name)
        filepath = os.path.join(self.keystores_workdir, name)

        if keystore_type == KeyStoreTypeEnum.password:
            if secret is None:
                # TODO: generate password
                raise NotImplementedError("Empty password is not supported")
            PasswordKeyStore.validate_password(secret)

            keystore = PasswordKeyStore.new(filepath=filepath, password=secret)
        elif keystore_type == KeyStoreTypeEnum.yubikey:
            keystore = YubikeyKeyStore.new(filepath=filepath, pin=secret)
        else:
            raise InvalidKeyStoreError("Invalid keystore type")

        if save:
            keystore.save()

        self.keystore_paths[name] = keystore.filepath

        return keystore

    def load_all(self):
        keystores = []
        for keystore in self.keystore_paths:
            keystore_path = os.path.join(self.keystores_workdir, keystore)
            keystores.append(self.__load_keystore_and_upgrade(keystore_path))

        return sorted(keystores, key=lambda keystore: keystore.name.casefold())

    def get_keystore(self, keystore_name: Optional[str], raise_none: bool = False,
                     upgrade: bool = True) -> Optional[BaseKeyStore]:
        if keystore_name is None:
            raise KeyStoreIsNotSpecifiedError("Keystore name is not specified.")

        keystore_name = self.__keystore_name(keystore_name)
        keystore_path = os.path.join(self.keystores_workdir, keystore_name)
        try:
            return self.__load_keystore_and_upgrade(keystore_path, upgrade)

        except (FileNotFoundError, IsADirectoryError):
            if raise_none:
                raise KeyStoreDoesNotExistError(
                    f"Keystore with the name '{keystore_name}' does not exist.")

            return None

        except json.JSONDecodeError as e:
            raise InvalidKeyStoreError("Invalid keystore file. " + str(e))

    @staticmethod
    def backup_keystore(keystore: BaseKeyStore, filepath: str, encrypted: bool = False):
        """
        Backup the keystore to a specified filepath.

        Args:
            keystore (BaseKeyStore): The keystore object to be backed up.
            filepath (str): The destination filepath where the backup will be saved.
            encrypted (bool, optional): Determines the backup format:
                - If True, the keystore will be copied as-is to the destination filepath.
                - If False, the keystore will be saved in an unencrypted JSON format.

        Notes:
            - The function does not check whether the destination path exists or not.
              If the file already exists, its content will be overwritten.
            - When `encrypted` is True, the keystore backup will be a direct copy of the keystore file
              to the specified filepath.
            - When `encrypted` is False, the keystore will be saved as an unencrypted JSON file using
              `KeystoreBackup.backup_json()`.
        """
        if encrypted:
            shutil.copy(keystore.filepath, filepath)
        else:
            storage.save_json(filepath, KeystoreBackup.backup_json(keystore))

    def restore_tons_keystore(self, name: str, filepath: str, keystore_type: KeyStoreTypeEnum,
                              secret: Optional[str] = None, encrypted: bool = False):
        """
        Restore a tons keystore from a backup file.

        Args:
            name (str): The name of the keystore (with or without the file extension).
            filepath (str): The path to the backup file.
            keystore_type (KeyStoreTypeEnum): The type of the keystore.
            secret (str, optional): The secret for the keystore. Not needed if `encrypted` is True.
            encrypted (bool, optional): Determines the backup format:
                - If True, the keystore file is stored as-is and copied to the keystore workdir under the new name.
                - If False, the keystore file is stored in a JSON format.

        Notes:
            - The function internally uses `__load_keystore_and_upgrade()`
              and `restore_unencrypted_keystore()` methods to handle the keystore restoration process.
            - When `encrypted` is True, the keystore file is simply copied into the keystore workdir
              under the new name. If the file already exists, its content will be overwritten.

        Raises:
            KeyStoreAlreadyExistsError: If a keystore with the same name already exists.
            KeyStoreNameInvalidError: If the keystore name is invalid.

        """
        if self.keystore_already_exists(name):
            raise KeyStoreAlreadyExistsError(name)

        if encrypted:
            try:
                self.__load_keystore_and_upgrade(filepath, upgrade=False)
            except InvalidKeyStoreError:
                raise
            else:
                name = self.__keystore_name(name)
                new_keystore_path = os.path.join(self.keystores_workdir, name)
                shutil.copy(filepath, new_keystore_path)
                self.keystore_paths[name] = new_keystore_path
        else:
            json_data = storage.read_json(filepath)
            self.restore_unencrypted_keystore(name, keystore_type, secret,
                                              KeystoreBackup.restore_from_tons(json_data))

    def restore_ton_cli_keystore(self, name: str, filepath: str, keystore_type,
                                 secret: Optional[str] = None):
        json_data = storage.read_json(filepath)
        self.restore_unencrypted_keystore(name, keystore_type, secret,
                                          KeystoreBackup.restore_from_ton_cli(json_data))

    @classmethod
    def unlock_keystore(cls, keystore, *, pin=None, password=None):
        if keystore.type == KeyStoreTypeEnum.yubikey:
            keystore.unlock(pin=pin)

    @classmethod
    def enter_sensitive(cls, keystore, *, pin=None, password=None):
        if keystore.type == KeyStoreTypeEnum.password:
            keystore.password = password

    def restore_unencrypted_keystore(self, name: str, keystore_type, secret: str, keystore_backup: KeystoreBackup):
        name = self.__keystore_name(name)

        keystore = self.create_new_keystore(name, keystore_type, secret, save=False)

        for backup_record in keystore_backup.records:
            keystore.add_new_record_from_secret(backup_record.name, backup_record.secret(), backup_record.version,
                                                backup_record.workchain, backup_record.subwallet_id,
                                                backup_record.comment, save=False, allow_empty_name=True)

        for backup_contact in keystore_backup.contacts:
            keystore.whitelist.add_contact(backup_contact.name, backup_contact.address,
                                           backup_contact.default_message, save=False)
        keystore.save()

        self.keystore_paths[name] = keystore.filepath

    # def load_encrypted_password_keystore_and_save_under_new_name(self,
    #                                                              file_path: str, backup_password: str,
    #                                                              new_name: str, new_password: str):
    #     """ TODO: Yubikey"""
    #     backup_keystore = self.get_keystore_from_path(file_path, upgrade=False)
    #     assert backup_keystore.type == KeyStoreTypeEnum.password
    #     backup_keystore.password = backup_password
    #
    #     keystore_json = KeystoreBackup.backup_json(backup_keystore)
    #     keystore_backup = KeystoreBackup.restore_from_tons(keystore_json)
    #     self.restore_unencrypted_keystore(new_name, KeyStoreTypeEnum.password, new_password, keystore_backup)

    @staticmethod
    def __keystore_name(name):
        ext = settings.KEYSTORE_FILE_EXT
        if not name.endswith(ext):
            name += ext
        return name

    def get_keystore_from_path(self, keystore_path: str, upgrade: bool = False) -> BaseKeyStore:
        return self.__load_keystore_and_upgrade(keystore_path, upgrade)

    def __load_keystore_and_upgrade(self, keystore_path: str, upgrade: bool = True) -> BaseKeyStore:
        """
        Loads a keystore from the specified path and performs an upgrade if the keystore is outdated.

        Args:
            keystore_path (str): The path from which the keystore is loaded.
            upgrade (bool, optional): Determines whether the keystore should be upgraded if outdated.
                                      If True (default), the keystore will be upgraded.
                                      If False, the keystore will not be modified.

        Returns:
            BaseKeyStore: The loaded keystore object. If an upgrade is performed, the backup information will be stored
            in the `upgrade_info` field of this object.

        Raises:
            InvalidKeyStoreError: If the keystore is broken or invalid.

        Notes:
            - The function reads the raw data from the keystore file and checks its integrity using an SHA-256 hash.
            - The keystore is then loaded and checked for its version. If an upgrade is required and `upgrade` is True,
              a backup is created before the upgrade process.
            - The upgraded keystore object is saved after the upgrade process.
        """
        raw_data = storage.read_bytes(keystore_path)
        if len(raw_data) < 32:
            raise InvalidKeyStoreError(f"Broken keystore: {keystore_path}")

        hash_data = raw_data[:32]
        data = raw_data[32:]
        if hash_data != sha256(data).digest():
            raise InvalidKeyStoreError(f"Broken keystore: {keystore_path}")

        json_data = json.loads(data.decode('utf-8'))
        json_data['filepath'] = keystore_path
        old_version = json_data["version"]
        assert isinstance(old_version, int)

        if old_version > settings.CURRENT_KEYSTORE_VERSION:
            raise InvalidKeyStoreError(f'Keystore {keystore_path} comes from a newer version of tons and '
                                       f'cannot be loaded. '
                                       'Please upgrade your version of tons.')

        if 'crypto' in json_data:
            if json_data['crypto']['type'] == KeyStoreTypeEnum.password:
                try:
                    keystore = PasswordKeyStore.load(json_data)
                except KeyError as exc:
                    raise InvalidKeyStoreError(f"Broken keystore: {keystore_path}. Key error: {str(exc)}")

            elif json_data['crypto']['type'] == KeyStoreTypeEnum.yubikey:
                try:
                    keystore = YubikeyKeyStore.load(json_data)
                except KeyError as exc:
                    raise InvalidKeyStoreError(f"Broken keystore: {keystore_path}. Key error: {str(exc)}")

            else:
                raise InvalidKeyStoreError(f"Broken keystore: {keystore_path}. Invalid type.")

        else:
            keystore = PasswordKeyStore.load(json_data)

        if old_version != keystore.version:
            if upgrade:
                keystore.set_upgraded(backup_path=self.__backup_before_upgrade(keystore_path), old_version=old_version)
                keystore.save()

        return keystore

    def __backup_before_upgrade(self, keystore_path) -> str:
        """
        Backup the keystore before upgrading.

        Args:
            keystore_path (str): Path to the keystore.

        Returns:
            str: Path to the created backup.
        """
        keystore_name = os.path.basename(keystore_path)
        backup_path = os.path.join(self.keystores_workdir, "backup",
                                   f"{time.strftime('%Y-%m-%d-%H-%M')}-{keystore_name}")
        storage.copy_file(keystore_path, backup_path)
        return backup_path

    @property
    def keystore_names(self) -> List[str]:
        return [self.strip_extension(keystore_name) for keystore_name in self.keystore_paths]

    @staticmethod
    def strip_extension(keystore_name: str) -> str:
        ext = settings.KEYSTORE_FILE_EXT
        if keystore_name.endswith(ext):
            keystore_name = keystore_name[:-len(ext)]
        return keystore_name


__all__ = [
    "KeyStores",
    "KeyStoreTypeEnum",
    "BaseKeyStore",
    "Record",
    "RecordBackup",
    "TonCliRecordBackup",
]
