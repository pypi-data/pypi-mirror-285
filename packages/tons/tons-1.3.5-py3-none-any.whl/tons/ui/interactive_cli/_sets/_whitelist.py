from collections import OrderedDict
from typing import Optional

import inquirer

from tons.tonclient.utils import BaseWhitelist, KeyStores, GlobalWhitelist, WhitelistContact, WhitelistContactType
from tons.tonsdk.utils import Address
from ._base import BaseSet, MenuItem
from ._mixin import KeyStoreMixin
from .._modified_inquirer import ModifiedConfirm, ListWithFilter, terminal
from .._utils import echo_success, processing
from .._validators import non_empty_string
from ..._utils import SharedObject, form_whitelist_table


class WhitelistSet(BaseSet, KeyStoreMixin):
    def __init__(self, ctx: SharedObject, whitelist: BaseWhitelist, whitelist_name=None) -> None:
        super().__init__(ctx)
        self.whitelist = whitelist
        if whitelist_name is not None:
            self._menu_message = f"Pick Whitelist command [{whitelist_name}]"

        self.whitelist_type = WhitelistContactType.local
        if not whitelist_name or whitelist_name == 'global':
            self.whitelist_type = WhitelistContactType.global_

    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}L{terminal.no_underline}ist contacts"] = \
            MenuItem(self._handle_list, "l")
        ord_dict[f"{terminal.underline}A{terminal.no_underline}dd contact"] = \
            MenuItem(self._handle_add, "a")
        ord_dict[f"{terminal.underline}M{terminal.no_underline}ove contact"] = \
            MenuItem(self._handle_move, "m")
        ord_dict[f"{terminal.underline}G{terminal.no_underline}et contact"] = \
            MenuItem(self._handle_get, "g")
        ord_dict[f"{terminal.underline}E{terminal.no_underline}dit contact"] = \
            MenuItem(self._handle_edit, "e")
        ord_dict[f"{terminal.underline}D{terminal.no_underline}elete contact"] = \
            MenuItem(self._handle_delete, "d")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_list(self):
        questions = [
            ModifiedConfirm(
                "verbose", message='Show balances?', default=True),
        ]
        verbose = self._prompt(questions)["verbose"]

        with processing():
            contacts = self.whitelist.get_contacts(self.ctx.config.tons.sort_whitelist)
            contact_infos = None
            if verbose:
                contact_infos = self.ctx.ton_client.get_addresses_information(
                    [contact.address for contact in contacts])

            table = form_whitelist_table(contacts, verbose, contact_infos)

        echo_success(table, only_msg=True)

    def _handle_add(self):
        questions = [
            inquirer.Text(
                "name", message='Enter the name', validate=non_empty_string),
            inquirer.Text(
                "address", message='Enter the address'),
            inquirer.Text(
                "message", message='Default message (press \'Enter\' to skip)'),
        ]
        ans = self._prompt(questions)
        name = ans["name"]
        address = ans["address"].strip()
        message = ans["message"]
        self.whitelist.add_contact(name, address, message, save=True)

        echo_success()

    def _handle_move(self):
        contact = self.__select_contact('Contact to move')
        if contact is None:
            return

        keystores = KeyStores(self.ctx.config.tons.keystores_path)
        choose_from = [keystore_name for keystore_name in self.ctx.keystores.keystore_paths.keys()
                       if keystore_name != self.ctx.keystore.name]

        whitelist_global_choice = "Whitelist (global)"
        if not isinstance(self.whitelist, GlobalWhitelist):
            choose_from = [whitelist_global_choice] + choose_from

        questions = [
            ListWithFilter(
                "move_to",
                message="Move to",
                choices=choose_from,
                carousel=True
            ),
            ModifiedConfirm(
                "remove_old", message="Remove contact from the current whitelist?", default=False),
        ]
        ans = self._prompt(questions)
        move_to = ans["move_to"]
        remove_old = ans["remove_old"]

        if move_to == whitelist_global_choice:
            whitelist = GlobalWhitelist(self.ctx.config.tons.whitelist_path)
        else:
            keystore_to_move_in = keystores.get_keystore(move_to, raise_none=True)
            self.unlock_keystore(keystore_to_move_in)
            whitelist = keystore_to_move_in.whitelist

        whitelist.add_contact(contact.name, contact.address, contact.default_message, True)

        if remove_old:
            self.whitelist.delete_contact(contact, True)

        echo_success()

    def _handle_get(self):
        contact = self.__select_contact('Contact to get')
        if contact is None:
            return

        addr = Address(contact.address)
        echo_success(
            f"Raw address: {addr.to_string(False, False, False)}", True)
        echo_success(
            f"Nonbounceable address: {addr.to_string(True, True, False)}", True)
        echo_success(
            f"Bounceable address: {addr.to_string(True, True, True)}", True)

    def _handle_edit(self):
        contact = self.__select_contact('Contact to edit')
        if contact is None:
            return

        new_name = self._select_whitelist_available_name(self.whitelist, contact.name)
        ans = self._prompt([
            inquirer.Text(
                "address", message='Enter new address', default=contact.address),
            inquirer.Text(
                "message", message='New default message (press \'Enter\' to skip)', default=contact.default_message),
        ])
        new_address = ans["address"].strip()
        new_message = ans["message"]

        self.whitelist.edit_contact(
            contact.name, new_name, new_address, new_message, save=True)

        echo_success()

    def _handle_delete(self):
        contact = self.__select_contact('Contact to delete')
        if contact is None:
            return

        self.whitelist.delete_contact(contact, save=True)

        echo_success()

    def __select_contact(self, message) -> Optional[WhitelistContact]:
        contacts = self.whitelist.get_contacts(self.ctx.config.tons.sort_whitelist)

        if not contacts:
            echo_success("You do not have any contacts yet.")
            return None

        questions = [
            ListWithFilter(
                "contact",
                message=message,
                choices=ListWithFilter.zip_choices_and_values(
                    [
                        WhitelistContact.pretty_string(contact.name, self.whitelist_type)
                        for contact in contacts
                    ],
                    contacts
                ),
                carousel=True
            )
        ]
        return self._prompt(questions)["contact"]
