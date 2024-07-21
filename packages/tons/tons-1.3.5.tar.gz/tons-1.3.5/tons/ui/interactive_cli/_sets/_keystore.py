import os
from abc import ABC
from collections import OrderedDict

import inquirer
from colorama import Fore

from tons.tonclient.utils import GlobalWhitelist, KeyStoreInvalidPasswordError
from tons.tonclient.utils._keystores import KeyStoreTypeEnum, PasswordKeyStore
from ._base import MenuItem, BaseSet
from ._dns import DNSSet
from ._jetton import JettonSet
from ._mixin import KeyStoreMixin, keystore_sensitive_area, KeystoreBackupFormat
from ._multisig import MultiSigSet
from ._tonconnect import TonconnectSet
from ._wallet import WalletSet
from ._whitelist import WhitelistSet
from .._modified_inquirer import ModifiedConfirm, ListWithFilter, terminal
from .._utils import echo_success, echo_error
from ..._utils import SharedObject, md_table, truncate, getcwd_pretty


class KeystoreBaseSet(ABC, BaseSet, KeyStoreMixin):
    def _get_secret(self, keystore_type): # TODO rename
        if keystore_type == KeyStoreTypeEnum.password:
            questions = [
                inquirer.Password(
                    "password1", message='Enter the password (at least 6 symbols)'),
                inquirer.Password(
                    "password2", message='Re-enter the password'),
            ]

            ans = self._prompt(questions)
            pass1 = ans["password1"]
            pass2 = ans["password2"]

            if self.__validate_passwords(pass1, pass2):
                return True, pass1

            return False, None

        elif keystore_type == KeyStoreTypeEnum.yubikey:
            questions = [
                inquirer.Password(
                    "pin", message='Enter Yubikey PIN'),
            ]

            return True, self._prompt(questions)['pin']

    @staticmethod
    def __validate_passwords(pass1, pass2):
        if pass1 != pass2:
            echo_error("Passwords do not match.")
            return False

        try:
            PasswordKeyStore.validate_password(pass1)
        except KeyStoreInvalidPasswordError as e:
            echo_error(str(e))
            return False

        return True



class KeystoreSet(KeystoreBaseSet):
    def __init__(self, ctx: SharedObject, keystore_name: str) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick command [{keystore_name}]"
        ctx.keystore = ctx.keystores.get_keystore(keystore_name, raise_none=True)

        self.unlock_keystore(ctx.keystore)

        ctx.whitelist = GlobalWhitelist(ctx.config.tons.whitelist_path)

    @property
    def starting_menu_pos(self):
        return 0

    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"W{terminal.underline}a{terminal.no_underline}llet"] = \
            MenuItem(self._handle_wallet, "a")
        ord_dict[f"{terminal.underline}W{terminal.no_underline}hitelist"] = \
            MenuItem(self._handle_local_whitelist, "w")
        ord_dict[f"{terminal.underline}M{terminal.no_underline}ultisig"] = \
            MenuItem(self._handle_multisig, "m")
        # ord_dict[f"Tonconnect {terminal.underline}v{terminal.no_underline}2"] = \
        #     MenuItem(self._handle_tonconnect, "v")
        ord_dict[f"D{terminal.underline}N{terminal.no_underline}S"] = \
            MenuItem(self._handle_dns, "n")
        # ord_dict[f"{terminal.underline}J{terminal.no_underline}etton"] = \
        #     MenuItem(self._handle_jetton, "j")
        ord_dict[f"Bac{terminal.underline}k{terminal.no_underline}up keystore"] = \
            MenuItem(self._handle_backup_keystore, "k")
        ord_dict[f"Ongoing tran{terminal.underline}s{terminal.no_underline}actions"] = \
            MenuItem(self._handle_pending, "s")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")

        return ord_dict

    def _handle_exit(self):
        if not self.ctx.background_task_manager.unfinished_tasks_remaining:
            super()._handle_exit()
            return
        echo_error("Please wait until all background tasks are finished.")

    def _handle_wallet(self):
        WalletSet(self.ctx).show()

    def _handle_multisig(self):
        MultiSigSet(self.ctx).show()

    def _handle_pending(self):
        table = md_table()
        table.field_names = ["Task", "Initiated", "Finished", "Status"]
        table.align["Task"] = 'l'
        for background_task in self.ctx.background_task_manager.tasks_list(unsafe=True):

            for result_description, description in zip(background_task.result_descriptions,
                                                       background_task.descriptions):
                result_description = truncate(result_description, max_len=100)
                result_description += Fore.RESET
                table.add_row([description,
                               background_task.time_start.strftime("%H:%M:%S"),
                               'in progress' if background_task.time_finish is None
                               else background_task.time_finish.strftime("%H:%M:%S"),
                               result_description])
        echo_success(str(table), only_msg=True)

    def _handle_backup_keystore(self):
        choices = [KeystoreBackupFormat.encrypted.value, KeystoreBackupFormat.unencrypted.value]
        values = [KeystoreBackupFormat.encrypted, KeystoreBackupFormat.unencrypted]
        backup_mode = self._prompt([
            ListWithFilter(
                'backup_mode',
                message='Select backup mode',
                choices=ListWithFilter.zip_choices_and_values(choices, values),
            )
        ])['backup_mode']

        ans = self._prompt([
            inquirer.Path("backup_file_path", path_type=inquirer.Path.FILE, exists=False,
                          message=f'Backup file path, file MUST not exist. (relative to {getcwd_pretty()})'),
            ModifiedConfirm(
                "is_sure",
                message='This will store keys in UNENCRYPTED FORM. '
                        'Are you sure you want to export unencrypted keys to disk?',
                default=False,
                ignore=backup_mode == KeystoreBackupFormat.encrypted
            ),
        ])
        backup_file_path = ans["backup_file_path"]
        is_sure = ans["is_sure"] or backup_mode == KeystoreBackupFormat.encrypted

        if os.path.exists(backup_file_path):
            if os.path.isdir(backup_file_path):
                echo_error(f'{backup_file_path} is a directory.')
                return
            is_sure &= self._prompt([
                ModifiedConfirm(
                    'sure_replace',
                    message='File already exists. Replace?',
                    default=False
                )
            ])['sure_replace']

        if not is_sure:
            echo_success("Action canceled.", True)
            return

        if backup_mode == KeystoreBackupFormat.unencrypted:
            if not self.ctx.keystore.type == KeyStoreTypeEnum.password:
                echo_error("Unencrypted backup process is only available "
                           "for password type keystores for security reasons")
                return

            self.__backup_unencrypted(backup_file_path)
        elif backup_mode == KeystoreBackupFormat.encrypted:
            self.__backup_encrypted(backup_file_path)

        echo_success()

    def _handle_local_whitelist(self):
        WhitelistSet(self.ctx,
                     self.ctx.keystore.whitelist,
                     self.ctx.keystore.name).show()

    def _handle_tonconnect(self):
        TonconnectSet(self.ctx).show()

    def _handle_dns(self):
        DNSSet(self.ctx).show()

    def _handle_jetton(self):
        JettonSet(self.ctx).show()

    @keystore_sensitive_area
    def __backup_unencrypted(self, dst_path: str):
        self.ctx.keystores.backup_keystore(self.ctx.keystore, dst_path, encrypted=False)

    def __backup_encrypted(self, dst_path: str):
        self.ctx.keystores.backup_keystore(self.ctx.keystore, dst_path, encrypted=True)
