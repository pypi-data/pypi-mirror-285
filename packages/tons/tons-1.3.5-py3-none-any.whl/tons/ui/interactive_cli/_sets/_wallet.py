import decimal
import os
from collections import OrderedDict
from copy import deepcopy
from typing import OrderedDict as OrderedDictTyping

import inquirer

from tons.tonclient._client._base import AddressState
from tons.tonclient.utils._exceptions import InvalidPrivateKeyError
from tons.tonsdk.contract.wallet import SendModeEnum, Wallets, WalletVersionEnum, WalletContract
from tons.tonsdk.crypto._payload_encryption import encrypt_message
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject, form_wallets_table, getcwd_pretty
from tons.ui.interactive_cli._sets._mixin import KeyStoreMixin
from tons.utils import storage
from ._base import BaseSet, MenuItem
from .._exceptions import InvalidBatchPattern
from .._modified_inquirer import TempText, ModifiedConfirm, RemovePrevAfterEnter, ListWithFilter, terminal
from .._utils import processing, echo_success, echo_error
from .._validators import ignore_if_transfer_all, number_greater_than_or_equal_to_zero, non_empty_string, \
    valid_mnemonics, integer_greater_than_zero, valid_workchain


class WalletSet(BaseSet, KeyStoreMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick Wallet command [{self.ctx.keystore.name}]"

    def _handlers(self) -> OrderedDictTyping[str, MenuItem]:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}L{terminal.no_underline}ist"] = \
            MenuItem(self._handle_list_wallets, "l")
        ord_dict[f"{terminal.underline}T{terminal.no_underline}ransfer"] = \
            MenuItem(self._handle_transfer, "t")
        ord_dict[f"{terminal.underline}A{terminal.no_underline}dvanced Transfer"] = \
            MenuItem(self._handle_advanced_transfer, "a")
        ord_dict[f"{terminal.underline}C{terminal.no_underline}reate"] = \
            MenuItem(self._handle_create_wallet, "c")
        ord_dict[f"{terminal.underline}M{terminal.no_underline}ove"] = \
            MenuItem(self._handle_move_wallet, "m")
        ord_dict[f"{terminal.underline}I{terminal.no_underline}nit"] = \
            MenuItem(self._handle_init_wallet, "i")
        ord_dict[f"{terminal.underline}G{terminal.no_underline}et"] = \
            MenuItem(self._handle_get_wallet, "g")
        ord_dict[f"{terminal.underline}E{terminal.no_underline}dit"] = \
            MenuItem(self._handle_edit_wallet, "e")
        ord_dict[f"{terminal.underline}D{terminal.no_underline}elete"] = \
            MenuItem(self._handle_delete_wallet, "d")
        ord_dict[f"{terminal.underline}R{terminal.no_underline}eveal mnemonics"] = \
            MenuItem(self._handle_reveal_wallet_mnemonics, "r")
        ord_dict[f"{terminal.underline}F{terminal.no_underline}rom mnemonics"] = \
            MenuItem(self._handle_import_from_mnemonics, "f")
        ord_dict[f"From {terminal.underline}p{terminal.no_underline}k"] = \
            MenuItem(self._handle_import_from_pk, "p")
        ord_dict[f"T{terminal.underline}o{terminal.no_underline} .addr and .pk"] = \
            MenuItem(self._handle_wallet_to_addr_pk, "o")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")

        return ord_dict

    def _handle_list_wallets(self):
        questions = [
            ModifiedConfirm(
                "verbose", message='Show verbose information?', default=True),
        ]
        verbose = self._prompt(questions)["verbose"]

        with processing():
            wallet_infos = None
            records = self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)
            if verbose:
                wallet_infos = self.ctx.ton_client.get_addresses_information(
                    [record.address for record in records])
            table = form_wallets_table(records, verbose, wallet_infos, True)

        echo_success(table, only_msg=True)

    def _handle_transfer(self):
        self.__handle_transfer(is_simple=True)

    def _handle_advanced_transfer(self):
        self.__handle_transfer(is_simple=False)

    def __handle_transfer(self, is_simple):
        from_wallet = self.select_wallet("Transfer from", verbose=True)
        if from_wallet is None:
            return

        record = self.ctx.keystore.get_record_by_name(
            from_wallet, raise_none=True)

        contact = self.select_contact("Send to", show_balance=True)
        if contact is None:
            return

        with processing():
            contact_info = self.ctx.ton_client.get_address_information(contact.address)

        if contact_info.state != AddressState.active:
            is_sure = self._prompt([
                ModifiedConfirm(
                    "is_sure", message="Sending to not active address. Send anyway?", default=False),
            ])["is_sure"]
            if not is_sure:
                echo_success("Action canceled.")
                return

        questions = [
            ModifiedConfirm("transfer_all", message='Transfer all remaining coins?',
                            default=False, ignore=is_simple),
            inquirer.Text("amount", message='Amount in TON coins to transfer',
                          ignore=ignore_if_transfer_all,
                          validate=number_greater_than_or_equal_to_zero),
            ModifiedConfirm(
                "destroy_if_zero", message='Destroy if balance becomes zero?',
                default=False, ignore=is_simple),
            inquirer.Text(
                "message", message='Message (press \'Enter\' to skip)', default=contact.default_message),
            ModifiedConfirm("encrypt_payload", message='Encrypt payload?',
                            default=False, ignore=is_simple or (not contact_info.is_wallet)
            ),
            ModifiedConfirm(
                "wait_for_result", message="Wait until transaction will be completed?", default=True),
        ]
        ans = self._prompt(questions)
        transfer_all = ans["transfer_all"]
        amount = 0 if transfer_all else decimal.Decimal(ans["amount"])
        message = ans["message"]
        destroy_if_zero = ans["destroy_if_zero"]
        wait_for_result = ans["wait_for_result"]
        encrypt_payload = ans["encrypt_payload"]

        send_mode = SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately
        if destroy_if_zero:
            send_mode |= SendModeEnum.destroy_account_if_zero
        if transfer_all:
            send_mode |= SendModeEnum.carry_all_remaining_balance

        wallet, secret = self.get_wallet_from_record(record)

        with processing():
            if encrypt_payload:
                if not contact_info.is_wallet:
                    echo_error(f"Contact cannot receive encrypted messages")
                    return

                message = encrypt_message(message, secret.public_key, contact_info.public_key, secret.private_key,
                                          wallet.address)

            task_id = self.ctx.background_task_manager.transfer_task(from_wallet=wallet,
                                                                     to_addr=contact.address,
                                                                     amount=amount,
                                                                     payload=message,
                                                                     send_mode=send_mode
                                                                     )
        if not wait_for_result:
            echo_success('Task has been added to the queue.')
            return

        self._wait_for_result_and_echo(task_id)

    def _handle_create_wallet(self):
        questions = [
            inquirer.List(
                "is_single", message="Choose option", choices=["Single", "Batch"],
                carousel=True),
            inquirer.List(
                "version", message='Wallet version', choices=[e.value for e in WalletVersionEnum],
                carousel=True, default=self.ctx.config.tons.default_wallet_version),
            inquirer.Text(
                "workchain", message='Workchain', default="0", validate=valid_workchain),
        ]
        ans = self._prompt(questions)
        is_single = ans["is_single"] == "Single"
        version = WalletVersionEnum(ans["version"])
        workchain = int(ans["workchain"])

        if is_single:
            questions = [
                inquirer.Text("name", message='Wallet name', validate=non_empty_string),
                inquirer.Text(
                    "comment", message='Wallet description (leave blank to skip)'),
            ]
            ans = self._prompt(questions)
            name = ans["name"]
            comment = ans["comment"]
            wallets_to_create = [(name, comment)]

        else:
            choices = ["Number of wallets and prefix",
                       "Pattern (e.g. 'My[5..87]Wallet' => My05Wallet, My06Wallet, ..., My87Wallet)"]
            batch_type = self._prompt([
                inquirer.List(
                    "batch_type", message="Batch type",
                    choices=choices,
                    carousel=True),
            ])["batch_type"]

            wallets_to_create = []

            if choices.index(batch_type) == 1:
                while True:
                    pattern = self._prompt([inquirer.Text("pattern", message="Pattern")])['pattern']
                    try:
                        prefix, suffix, begin_idx, end_idx, idx_length = self._parse_batch_pattern(pattern)
                    except InvalidBatchPattern as exc:
                        self._explain_invalid_batch_pattern(exc)
                    else:
                        break

                comment = self._prompt([
                    inquirer.Text(
                        "comment", message='Overall wallets description (leave blank to skip)'),
                ])['comment']

                for num in range(begin_idx, end_idx + 1):
                    number = str(num).zfill(idx_length)
                    wallets_to_create.append((f"{prefix}{number}{suffix}", comment))

            else:
                questions = [
                    inquirer.Text("number_of_wallets",
                                  message="Number of wallets to create",
                                  validate=integer_greater_than_zero),
                    inquirer.Text(
                        "prefix", message='Wallet name prefix (e.g. employee_)'),
                    inquirer.Text(
                        "comment", message='Overall wallets description (leave blank to skip)'),
                ]
                ans = self._prompt(questions)
                number_of_wallets = int(ans["number_of_wallets"])
                prefix = ans["prefix"]
                comment = ans["comment"]

                for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore):
                    if record.name.startswith(prefix):
                        name = record.name[len(prefix):]
                        try:
                            int(name)
                            echo_error(f"Wallets with the prefix '{prefix}' already exist")
                            return

                        except ValueError:
                            pass
                leading_zeros = len(str(number_of_wallets))
                i = 1
                while len(wallets_to_create) < number_of_wallets:
                    wallet_name_unique = False
                    new_name = None
                    while not wallet_name_unique:
                        new_name = f"{prefix}{str(i).zfill(leading_zeros)}"
                        i += 1
                        if self.ctx.keystore.get_record_by_name(new_name) is not None:
                            continue
                        wallet_name_unique = True

                    wallets_to_create.append((new_name, comment))

        if not is_single:
            msg = f"Create '{wallets_to_create[0][0]}'-'{wallets_to_create[-1][0]}' wallets?"
            is_sure = self._prompt([
                ModifiedConfirm(
                    "is_sure", message=msg,
                    default=True), ])["is_sure"]
            if not is_sure:
                echo_success("Action canceled.")
                return

        with processing():
            subwallet_id = WalletContract.default_subwallet_id(workchain, version)
            with self.ctx.keystore.restore_on_failure():
                for wallet_name, comment in wallets_to_create:
                    mnemonics, _, _, _ = Wallets.create(version, workchain, subwallet_id)
                    self.ctx.keystore.add_new_record(wallet_name, mnemonics, version,
                                                     workchain, subwallet_id, comment, save=False)
                self.ctx.keystore.save()

        echo_success()

    @classmethod
    def _explain_invalid_batch_pattern(cls, exception: InvalidBatchPattern):
        echo_error(f"{exception}\n\n"
                   "Expected: PREFIX[BEGIN..END]SUFFIX.\n\n"
                   "Example: wallet-[51..107]-abc\n"
                   "Result: wallet-51-abc, wallet-52-abc, ..., wallet-107-abc")

    @classmethod
    def _parse_batch_pattern(cls, pattern: str) -> [str, str, int, int, int]:
        """
        Parses a batch pattern.

        Returns:
            Tuple[str, str, int, int]: A tuple containing the parsed components of the batch pattern.
                - str: Prefix of the batch pattern.
                - str: Suffix of the batch pattern.
                - int: Starting index of the batch pattern.
                - int: Ending index of the batch pattern.
                - int: Number of characters reserved for index.

        Example:
            >> WalletSet._parse_batch_pattern('My[5..100]wallet')
            ('My', 'wallet', 5, 100, 3)

        Raises:
            InvalidBatchPattern: If the provided pattern does not match the expected format.
                - The pattern must contain exactly one "[" and exactly one "]".
                - Invalid range format: "X..Y". Expected: X..Y, where X and Y are integer numbers, X <= Y.
        """
        try:
            prefix, tmp = pattern.split('[')
            range_, suffix = tmp.split(']')
            del tmp
        except ValueError as _exc:
            raise InvalidBatchPattern('The pattern must contain exactly one "[" and exactly one "]"')

        try:
            begin_idx, end_idx = range_.split('..')
            idx_length = max(map(len, [begin_idx, end_idx]))
            begin_idx, end_idx = int(begin_idx), int(end_idx)
            assert begin_idx <= end_idx
        except (ValueError, TypeError, AssertionError) as _exc:
            raise InvalidBatchPattern(f'Invalid range: "{range_}". '
                                      f'Expected: X..Y, where X and Y are integers, X <= Y')

        return prefix, suffix, begin_idx, end_idx, idx_length

    def _handle_move_wallet(self):
        wallet_name = self.select_wallet("Move wallet")
        if wallet_name is None:
            return
        record = self.ctx.keystore.get_record_by_name(wallet_name, raise_none=True)

        choose_from = [keystore_name for keystore_name in self.ctx.keystores.keystore_paths.keys()
                       if keystore_name != self.ctx.keystore.name]

        questions = [
            ListWithFilter(
                "move_to",
                message="Move to",
                choices=choose_from,
                carousel=True
            ),
            ModifiedConfirm(
                "remove_old", message="Remove wallet from the current keystore?", default=False),
        ]
        ans = self._prompt(questions)
        move_to = ans["move_to"]
        remove_old = ans["remove_old"]

        keystore_to_move_in = self.ctx.keystores.get_keystore(move_to, raise_none=True)
        self.unlock_keystore(keystore_to_move_in)
        _, secret = self.get_wallet_from_record(record)

        keystore_to_move_in.add_new_record_from_secret(
            record.name,
            secret,
            record.version,
            record.workchain,
            record.subwallet_id,
            record.comment,
            save=True
        )

        if remove_old:
            self.ctx.keystore.delete_record(record.name, save=True)

        echo_success()

    def _handle_init_wallet(self):
        wallet_name_to_init = self.select_wallet("Wallet to init")
        if wallet_name_to_init is None:
            return
        questions = [
            ModifiedConfirm(
                "wait_for_result", message="Wait until transaction will be completed?", default=True),
        ]
        ans = self._prompt(questions)
        wait_for_result = ans["wait_for_result"]
        record = self.ctx.keystore.get_record_by_name(wallet_name_to_init, raise_none=True)

        with processing():
            address_info = self.ctx.ton_client.get_address_information(record.address)

        if address_info.state == AddressState.active:
            echo_error("Wallet is already active.")
            return
        if address_info.balance < (init_amount := WalletContract.init_amount(record.version)):
            echo_error(f"Insufficient amount, at least {init_amount} required.")
            return

        wallet, _ = self.get_wallet_from_record(record)

        with processing():
            task_id = self.ctx.background_task_manager.deploy_wallet_task(wallet)

        if not wait_for_result:
            echo_success("Transaction has been queued.")
            return

        self._wait_for_result_and_echo(task_id)

    def _handle_get_wallet(self):
        wallet_name = self.select_wallet("Get wallet")
        if wallet_name is None:
            return

        wallet = self.ctx.keystore.get_record_by_name(wallet_name, raise_none=True)

        questions = [
            ModifiedConfirm(
                "verbose", message='Show balances?', default=True),
        ]
        verbose = self._prompt(questions)["verbose"]

        addr = Address(wallet.address)

        if verbose:
            with processing():
                addr_info = self.ctx.ton_client.get_address_information(wallet.address)

        echo_success(
            f"Raw address: {addr.to_string(False, False, False)}", True)
        echo_success(
            f"Nonbounceable address: {addr.to_string(True, True, False)}", True)
        echo_success(
            f"Bounceable address: {addr.to_string(True, True, True)}", True)
        echo_success(f"Version: {wallet.version}", True)
        echo_success(f"Workchain: {wallet.workchain}", True)
        echo_success(f"Subwallet id: {wallet.subwallet_id}", True)
        echo_success(f"Comment: {wallet.comment}", True)

        if verbose:
            echo_success("--- Verbose wallet information ---", True)
            for k, v in addr_info.dict().items():
                if isinstance(v, AddressState):
                    v = v.value
                echo_success(str(k) + ': ' + str(v), True)

    def _handle_edit_wallet(self):
        wallet_name = self.select_wallet("Edit wallet")
        if wallet_name is None:
            return

        record = self.ctx.keystore.get_record_by_name(wallet_name)
        old_comment = record.comment

        new_name = self._select_wallet_available_name(wallet_name)
        if new_name is None:
            return

        new_comment = self._prompt([
            inquirer.Text(
                "new_comment", message='New wallet description', default=old_comment),
        ])["new_comment"]

        self.ctx.keystore.edit_record(wallet_name, new_name, new_comment, save=True)

        echo_success()

    def _handle_delete_wallet(self):
        wallet_name = self.select_wallet("Delete wallet")
        if wallet_name is None:
            return

        confirm_phrase = f'Are you sure you want to delete {wallet_name} wallet?'
        names_to_delete = [wallet_name]

        is_sure = self._prompt([
            ModifiedConfirm(
                "is_sure", message=confirm_phrase, default=False),
        ])["is_sure"]
        if not is_sure:
            echo_success("Action canceled.", True)
            return

        with self.ctx.keystore.restore_on_failure():
            for name in names_to_delete:
                self.ctx.keystore.delete_record(name, save=False)
            self.ctx.keystore.save()

        echo_success()

    def _handle_reveal_wallet_mnemonics(self):
        wallet_name = self.select_wallet("Wallet to reveal")
        if wallet_name is None:
            return

        record = self.ctx.keystore.get_record_by_name(
            wallet_name, raise_none=True)

        _, secret = self.get_wallet_from_record(record)
        if not secret.mnemonics:
            echo_error("Mnemonics are not available for this wallet (likely imported from PK).")
            return

        mnemonics = secret.mnemonics.split()

        text_to_erase = ""
        for i in range(4):
            mnemonics_row = " ".join(mnemonics[i * 6:i * 6 + 6])
            echo_success(mnemonics_row, only_msg=True)
            text_to_erase += f"{mnemonics_row}\n"

        self._prompt([
            RemovePrevAfterEnter("_",
                                 text_to_erase=text_to_erase,
                                 message="Press 'Enter' to remove mnemonics from the screen")
        ])

    def _handle_import_from_mnemonics(self):
        mnemonics = self._prompt([TempText("mnemonics", message="Mnemonic words (separated by spaces)",
                                           validate=valid_mnemonics)])["mnemonics"].split(" ")

        questions = [
            inquirer.List(
                "version", message='Wallet version', choices=[e.value for e in WalletVersionEnum],
                carousel=True, default=self.ctx.config.tons.default_wallet_version),
            inquirer.Text(
                "workchain", message='Workchain', default="0"),
            inquirer.Text("name", message='Wallet name', validate=non_empty_string)
        ]
        ans = self._prompt(questions)
        version = WalletVersionEnum(ans["version"])
        workchain = int(ans["workchain"])
        name = ans["name"]

        questions = [
            inquirer.Text(
                "comment", message='Wallet description (leave blank to skip)')
        ]
        ans = self._prompt(questions)
        comment = ans["comment"]
        subwallet_id = WalletContract.default_subwallet_id(workchain, version)
        self.ctx.keystore.add_new_record(name, mnemonics, version,
                                         workchain, subwallet_id, comment, save=True)

        echo_success()

    def _handle_import_from_pk(self):
        questions = [
            inquirer.Path("pk_path", path_type=inquirer.Path.FILE, exists=True,
                          message=f'Path to pk (relative to {getcwd_pretty()})'),
            inquirer.List(
                "version", message='Wallet version', choices=[e.value for e in WalletVersionEnum],
                carousel=True, default=self.ctx.config.tons.default_wallet_version),
            inquirer.Text(
                "workchain", message='Workchain', default="0"),
            inquirer.Text("name", message='Wallet name', validate=non_empty_string)
        ]
        ans = self._prompt(questions)
        pk_path = ans['pk_path']
        version = WalletVersionEnum(ans["version"])
        workchain = int(ans["workchain"])
        name = ans["name"]

        questions = [
            inquirer.Text(
                "comment", message='Wallet description (leave blank to skip)')
        ]
        ans = self._prompt(questions)
        comment = ans["comment"]
        subwallet_id = WalletContract.default_subwallet_id(workchain, version)
        with open(pk_path, 'rb') as f:
            pk = f.read()

        try:
            self.ctx.keystore.add_new_record_from_pk(name, pk, version, workchain, subwallet_id, comment, save=True)
        except InvalidPrivateKeyError as exc:
            echo_error(f"Invalid private key ({str(exc)})")
        else:
            echo_success()

    def _handle_wallet_to_addr_pk(self):
        wallet_name = self.select_wallet("Wallet to use")
        if wallet_name is None:
            return
        questions = [
            inquirer.Text("destination_dir",
                          message='Directory path to export into'),
        ]
        ans = self._prompt(questions)
        destination_dir = ans["destination_dir"]

        record = self.ctx.keystore.get_record_by_name(
            wallet_name, raise_none=True)

        wallet, secret = self.get_wallet_from_record(record)
        addr_path = os.path.join(
            destination_dir, record.name + ".addr")
        pk_path = os.path.join(destination_dir, record.name + ".pk")
        addr = Address(wallet.address).to_buffer()
        pk = secret.private_key[:32]
        storage.save_bytes(addr_path, addr)
        storage.save_bytes(pk_path, pk)
        echo_success()


