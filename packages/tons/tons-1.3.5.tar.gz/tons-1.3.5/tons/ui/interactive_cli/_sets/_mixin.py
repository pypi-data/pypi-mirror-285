import contextlib
import decimal
from enum import Enum
from typing import List, Callable, Optional, Tuple

import inquirer

from tons.tonclient.utils import KeyStoreTypeEnum, KeyStores, KeyStoreInvalidPasswordError, WhitelistContact, \
    WhitelistContactType, Record
from tons.tonclient.utils._keystores._keystore._secret import WalletSecretKind, WalletSecret
from tons.tonsdk.contract.wallet import WalletContract
from tons.tonsdk.utils import Address
from .._modified_inquirer import ModifiedPrompt, ListWithFilter
from .._utils import echo_error, echo_success, processing
from .._validators import non_empty_string
from ..._utils import SharedObject


class KeyStoreNotSelected(Exception):
    pass


class KeystoreBackupFormat(str, Enum):
    encrypted = 'Encrypted'
    unencrypted = 'Unencrypted'


def requires_keystore_selected(nonstatic_method: Callable):
    def magic(self: 'KeyStoreMixin', *args, **kwargs):
        if self.ctx.keystore is None:
            raise KeyStoreNotSelected
        return nonstatic_method(self, *args, **kwargs)

    return magic


def keystore_sensitive_area(nonstatic_method: Callable):
    @requires_keystore_selected
    def magic(self: 'KeyStoreMixin', *args, **kwargs):
        if self.ctx.keystore.type == KeyStoreTypeEnum.password:
            while True:
                questions = [inquirer.Password("keystore_password", message=f'{self.ctx.keystore.name} password')]
                try:
                    with self.password(self._prompt(questions)["keystore_password"]):
                        return nonstatic_method(self, *args, **kwargs)
                except KeyStoreInvalidPasswordError as e:
                    echo_error(str(e))
                    continue
        return nonstatic_method(self, *args, **kwargs)

    return magic


class KeyStoreMixin(ModifiedPrompt):
    ctx: SharedObject

    @staticmethod
    def unlock_keystore(keystore):
        if keystore.type == KeyStoreTypeEnum.yubikey:
            questions = [inquirer.Password("pin", message='Yubikey PIN')]
            pin = KeyStoreMixin._prompt(questions)["pin"]
            KeyStores.unlock_keystore(keystore, pin=pin)

    @keystore_sensitive_area
    def get_wallet_from_record(self, record) -> Tuple[WalletContract, WalletSecret]:
        return self.ctx.keystore.get_wallet_from_record(record)

    @contextlib.contextmanager
    @requires_keystore_selected
    def password(self, _password: str):
        self.ctx.keystore.password = _password
        try:
            yield
        finally:
            self.ctx.keystore.password = None

    @staticmethod
    def add_mask_and_balance(name, mask=None, balance: Optional[decimal.Decimal] = None) -> str:
        """
        Adds a mask and balance information to a `name` string.

        Takes a name string and optionally adds a mask and balance information to it. The resulting string includes
        the name, followed by the mask and balance (if provided) enclosed in square brackets.

        Args:
            name: The name string to which the mask and balance information will be added.
            mask (optional): The mask information to be included.
            balance (optional): The balance information to be included.

        Returns:
            str: The modified name string with the mask and balance information.

        Example:
            result = KeyStoreMixin.add_mask_and_balance("John Doe", mask="ABC123", balance=1000)
            # The value of `result` will be: "John Doe [ABC123 1000]"

            result = ExampleClass.add_mask_and_balance("Jane Smith", mask="QWERTY")
            # The value of `result` will be: "Jane Smith [QWERTY]"
        """
        if balance is not None:
            balance = format(balance, 'f')
        in_brackets = [str(s) for s in (mask, balance) if s is not None]
        result = str(name)
        if len(in_brackets) > 0:
            result += f' [{" ".join(in_brackets)}]'
        return result

    def select_contact(self, message: str, show_balance=False) -> WhitelistContact:
        """
        Prompt the user to select a contact.

        This method presents a menu to the user with a list of contacts to choose from.
        The user can select a contact from the menu, or add a new contact if desired.

        Args:
            message (str): The message to be displayed to the user.
            show_balance (bool): Flag indicating whether to display balance information for the contacts.
            Default is False.

        Returns:
            WhitelistContact: The selected WhitelistContact object representing the chosen contact.

        Notes:
            - The user can select from local contacts, global contacts and keystore wallets.
            - The new contact created via "(add new)" command is added to the local whitelist.
            - If `show_balance` is True, an additional request is performed to fetch the balances using the
              `ton_client.get_addresses_information()` method.

        """
        choices, values = self.__get_contact_selection_for_menu(show_balance)
        local_whitelist = self.ctx.keystore.whitelist

        while True:
            questions = [
                ListWithFilter(
                    "contact",
                    message=message,
                    choices=ListWithFilter.zip_choices_and_values(choices, values),
                    carousel=True
                )
            ]
            selected_contact = self._prompt(questions)["contact"]
            if selected_contact is not None:
                break

            questions = [
                inquirer.Text("name", message='Enter the name', validate=non_empty_string),
                inquirer.Text("address", message='Enter the address'),
                inquirer.Text("message", message='Default message (press \'Enter\' to skip)'),
            ]
            answer = self._prompt(questions)
            local_whitelist.add_contact(answer["name"],
                                        answer["address"].strip(),
                                        answer["message"],
                                        save=True)
            choices, values = self.__get_contact_selection_for_menu(show_balance)
            echo_success()

        return selected_contact

    def __get_contact_selection_for_menu(self, show_balance: bool) -> \
            Tuple[Tuple[str, ...], Tuple[Optional[WhitelistContact], ...]]:
        local_contacts = \
            self.ctx.keystore.whitelist.get_contacts(self.ctx.config.tons.sort_whitelist)
        local_contacts_names = \
            tuple(WhitelistContact.pretty_string(contact.name, WhitelistContactType.local)
                  for contact in local_contacts)

        global_contacts = \
            self.ctx.whitelist.get_contacts(self.ctx.config.tons.sort_whitelist)
        global_contacts_names = \
            tuple(WhitelistContact.pretty_string(contact.name, WhitelistContactType.global_)
                  for contact in global_contacts)

        records_contacts = \
            tuple(WhitelistContact(name=record.name, address=record.tep_standard_user_address)
                  for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore))
        records_names = \
            tuple(WhitelistContact.pretty_string(contact.name, WhitelistContactType.keystore)
                  for contact in records_contacts)

        multisig_contacts = \
            tuple(WhitelistContact(name=multisig.name, address=multisig.address)
                  for multisig in self.ctx.keystore.multisig_wallet_list.get_records())
        multisig_names = \
            tuple(multisig.pretty_string()
                  for multisig in self.ctx.keystore.multisig_wallet_list.get_records()
            )

        pretty_names: Tuple[str, ...] = records_names + local_contacts_names + global_contacts_names + multisig_names
        contacts: Tuple[WhitelistContact, ...] = records_contacts + local_contacts + global_contacts + multisig_contacts

        balances = (None,) * len(contacts)
        if show_balance:
            with processing():
                contacts_infos = \
                    self.ctx.ton_client.get_addresses_information([contact.address for contact in contacts])
            balances = tuple(contact_info.balance for contact_info in contacts_infos)

        pretty_names = \
            tuple(self.add_mask_and_balance(name, Address(contact.address).to_mask(only_friendly=True), balance)
                  for name, contact, balance
                  in zip(pretty_names, contacts, balances))

        return ('(add new)',) + pretty_names, (None,) + contacts

    def select_wallet(self, message,
                      verbose=False, *,
                      filter_: Optional[Callable[[Record], bool]] = None,
                      no_wallets_message: str = "You do not have any wallets yet.") -> Optional[str]:
        records = self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)
        if not records:
            echo_success(no_wallets_message)
            return None

        if filter_:
            records = tuple(filter(filter_, records))

        record_values = [record.name for record in records]
        if verbose:
            with processing():
                wallet_infos = self.ctx.ton_client.get_addresses_information(
                    [record.address for record in records])
                record_choices = [
                    self.add_mask_and_balance(record.name, Address(record.address).to_mask(), wallet_info.balance)
                    for record, wallet_info in zip(records, wallet_infos)]
        else:
            record_choices = record_values.copy()
        record_choices = [WhitelistContact.pretty_string(record, WhitelistContactType.keystore)
                          for record in record_choices]
        questions = [
            ListWithFilter(
                "wallet",
                message=message,
                choices=ListWithFilter.zip_choices_and_values(record_choices, record_values),
                carousel=True,
            )
        ]
        return self._prompt(questions)["wallet"]
