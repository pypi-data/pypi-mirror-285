from collections import OrderedDict

import inquirer

from tons.tonclient.utils import KeyStores
from tons.tonclient.utils._keystores import KeyStoreTypeEnum
from ._base import MenuItem
from ._keystore import KeystoreSet, KeystoreBaseSet
from ._mixin import KeystoreBackupFormat
from .._modified_inquirer import ListWithFilter, terminal
from .._utils import echo_success, echo_warning, echo_error, processing
from .._validators import non_empty_string
from ..._utils import SharedObject, getcwd_pretty


class KeystoresSet(KeystoreBaseSet):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self.ctx.keystores = KeyStores(
            self.ctx.config.tons.keystores_path)

    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}O{terminal.no_underline}pen keystore"] = \
            MenuItem(self._handle_open_keystore, "o")
        ord_dict[f"{terminal.underline}C{terminal.no_underline}reate keystore"] = \
            MenuItem(self._handle_create_keystore, "c")
        ord_dict[f"{terminal.underline}R{terminal.no_underline}estore keystore"] = \
            MenuItem(self._handle_restore_keystore, "r")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_open_keystore(self):
        if self.ctx.keystores.keystore_paths:
            while True:
                with processing():
                    keystore_list = self.ctx.keystores.load_all()

                for keystore in keystore_list:
                    if keystore.has_been_upgraded:
                        echo_warning(f"Keystore '{keystore.name}' has been upgraded "
                                     f"from version {keystore.upgrade_info.old_version} "
                                     f"to version {keystore.version}.")
                        echo_warning(f"Old version has been saved to {keystore.upgrade_info.backup_path}")

                keystore_choices = [keystore.pretty_string() for keystore in keystore_list]
                keystore_choices += ["Back"]

                keystore_values = [keystore.name for keystore in keystore_list]
                keystore_values += [None]

                keystore_name = self._prompt([
                    ListWithFilter("keystore_name", message="Choose keystore to use",
                                   choices=ListWithFilter.zip_choices_and_values(keystore_choices, keystore_values),
                                   carousel=True),
                ])["keystore_name"]

                if keystore_name is None:
                    break

                KeystoreSet(self.ctx, keystore_name).show()
        else:
            echo_success("You do not have any keystores yet.")

    def _handle_create_keystore(self):
        questions = [
            inquirer.Text(
                "name", message='Enter the name', validate=non_empty_string),
            inquirer.List(
                "keystore_type", message='Keystore type', choices=[KeyStoreTypeEnum.password],
                carousel=True),
        ]
        ans = self._prompt(questions)
        name = ans["name"]
        keystore_type = ans["keystore_type"]

        if self.ctx.keystores.keystore_already_exists(name):
            echo_error(f"Keystore with the name '{name}' already exists")
            return

        success, secret = self._get_secret(keystore_type)
        if success:
            self.ctx.keystores.create_new_keystore(name, keystore_type, secret,
                                                   save=True)
            echo_success()

    def _handle_restore_keystore(self):
        ans = self._prompt([
            inquirer.List("restore_from", message='Restore from',
                          choices=["tons backup", "ton-cli backup"]),
            inquirer.Path(
                "backup_file_path", path_type=inquirer.Path.FILE, exists=True,
                message=f'Backup file path (relative to {getcwd_pretty()})'),
        ])
        restore_from = ans["restore_from"]
        backup_file_path = ans["backup_file_path"]

        ans = self._prompt([
            inquirer.Text(
                "name", message="Enter new keystore name", validate=non_empty_string),
            ListWithFilter('backup_type',
                           message='Select backup type',
                           carousel=True,
                           ignore=restore_from == "ton-cli backup",
                           default=KeystoreBackupFormat.encrypted,
                           choices=[KeystoreBackupFormat.encrypted, KeystoreBackupFormat.unencrypted]),
            inquirer.List("keystore_type", message='New keystore type', choices=[KeyStoreTypeEnum.password],
                          ignore=lambda answers: answers["backup_type"] == KeystoreBackupFormat.encrypted,
                          default=KeyStoreTypeEnum.password,
                          carousel=True),
        ])
        name = ans["name"]
        backup_type = ans["backup_type"]
        keystore_type = ans["keystore_type"]

        if self.ctx.keystores.keystore_already_exists(name):
            echo_error(f"Keystore with the name {name} already exists")

        if restore_from == "ton-cli backup":
            success, secret = self._get_secret(keystore_type)
            if not success:
                return

            self.ctx.keystores.restore_ton_cli_keystore(
                name, backup_file_path, keystore_type, secret)
        elif restore_from == "tons backup":
            secret = None
            if backup_type == KeystoreBackupFormat.unencrypted:
                success, secret = self._get_secret(keystore_type)
                if not success:
                    return

            self.ctx.keystores.restore_tons_keystore(
                name, backup_file_path, keystore_type, secret, backup_type == KeystoreBackupFormat.encrypted)
        echo_success()
