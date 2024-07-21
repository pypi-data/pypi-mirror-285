import decimal
from collections import OrderedDict
from typing import OrderedDict as OrderedDictTyping, Optional, Tuple

import inquirer

from tons.tonclient import JettonMinterResult, JettonWalletResult
from tons.tonclient.utils import Record
from tons.tonsdk.contract.wallet import Wallets
from tons.tonsdk.utils import Address
from ._base import BaseSet, MenuItem
from ._mixin import KeyStoreMixin
from .._modified_inquirer import terminal, ListWithFilter, ModifiedConfirm
from .._utils import echo_success, echo_error, processing
from ..._utils import SharedObject, md_table, fetch_known_jettons_addresses


class JettonSet(BaseSet, KeyStoreMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick Jetton command [{self.ctx.keystore.name}]"

    def _handlers(self) -> OrderedDictTyping[str, MenuItem]:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}T{terminal.no_underline}ransfer"] = \
            MenuItem(self._handle_transfer, "t")
        ord_dict[f"{terminal.underline}L{terminal.no_underline}ist"] = \
            MenuItem(self._handle_list, "l")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_transfer(self) -> None:
        with processing():
            addresses = [record.address for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)]
            jetton_minters, jetton_wallets = self.ctx.ton_client.get_jetton_information(addresses)
            known_minters = fetch_known_jettons_addresses()

        jetton_wallet_map = _get_jetton_wallet_map(jetton_wallets)
        jetton_minters = _sorted_minters(jetton_minters)

        symbol_max_len = max(len(str(minter.metadata.symbol)) for minter in jetton_minters) if jetton_minters else 0
        choices = [self.__menufy_jetton_minter(minter, symbol_max_len, known_minters) for minter in jetton_minters]
        if len(choices) == 0:
            echo_success('You do not own any Jettons.')
            return

        questions = [
            ListWithFilter(
                "Jetton",
                message="Select Jetton",
                choices=ListWithFilter.zip_choices_and_values(choices, jetton_minters),
                carousel=True
            )
        ]
        selected_minter: JettonMinterResult = self._prompt(questions)['Jetton']
        wallets_of_selected_minter = jetton_wallet_map[selected_minter.account.address]
        choices = [self.__menufy_jetton_wallet(wallet, selected_minter) for wallet in wallets_of_selected_minter]
        prompt_symbol = selected_minter.metadata.symbol + ' ' if selected_minter.metadata.symbol is not None else ''
        questions = [
            ListWithFilter(
                "wallet",
                message=f"Transfer {prompt_symbol}from",
                choices=ListWithFilter.zip_choices_and_values(choices, wallets_of_selected_minter),
                carousel=True
            )
        ]
        selected_jetton_wallet: JettonWalletResult = self._prompt(questions)['wallet']

        owner_record = self.ctx.keystore.get_record_by_address(Address(selected_jetton_wallet.owner_address))
        with processing():
            owner_address_info = self.ctx.ton_client.get_address_information(owner_record.address)
        if owner_address_info.balance < self.ctx.config.jetton.gas_amount:
            echo_error(f'Insufficient TONs on {owner_record.name} for Jetton transaction. '
                       f'Expected at least {self.ctx.config.jetton.gas_amount}.')
            return

        contact = self.select_contact(f"Send {prompt_symbol}to", show_balance=False)
        if contact is None:
            return

        while True:
            questions = [inquirer.Text("amount",
                                       message=f'Amount {"in " + prompt_symbol if prompt_symbol else ""}to transfer')]
            try:
                amount = decimal.Decimal(self._prompt(questions)['amount'])
                balance = selected_jetton_wallet.balance_readable(selected_minter.metadata)
                if amount > balance:
                    echo_error(f"Insufficient {prompt_symbol}balance for this transaction")
                    return
            except ValueError:
                echo_error("Invalid amount")
            else:
                break

        questions = [ModifiedConfirm("wait_for_result",
                                     message="Wait until transaction will be completed?", default=True)]
        wait_for_result = self._prompt(questions)['wait_for_result']

        with processing():
            contact_info = self.ctx.ton_client.get_address_information(contact.address)

        record = self.ctx.keystore.get_record_by_address(Address(selected_jetton_wallet.owner_address), raise_none=True)
        self.__transfer_jetton(Address(contact_info.address), record, amount, selected_jetton_wallet, selected_minter,
                               wait_for_result)

    def _handle_list(self):
        if not self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore):
            echo_success("You do not have any wallets yet.")
            return
        records = self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)
        choices = ['(all)'] + [self.add_mask_and_balance(record.name, Address(record.address).to_mask(), None)
                               for record in records]
        values = (None,) + records

        questions = [
            ListWithFilter(
                "wallet",
                message="Select wallet",
                choices=ListWithFilter.zip_choices_and_values(choices, values),
                carousel=True
            )
        ]
        wallet: Optional[Record] = self._prompt(questions)["wallet"]

        if wallet is None:
            addresses = [record.address for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)]
        else:
            addresses = [wallet.address]

        with processing():
            jetton_minters, jetton_wallets = self.ctx.ton_client.get_jetton_information(addresses)
            known_minters = fetch_known_jettons_addresses()

        jetton_wallet_map = _get_jetton_wallet_map(jetton_wallets)
        jetton_minters = _sorted_minters(jetton_minters)

        jetton_table = md_table()
        field_names = []
        if wallet is None:
            field_names += ['Wallet', 'Mask']

        if known_minters:
            field_names += ['Known']
        field_names += ['Symbol', 'Name', 'Balance']
        field_names += ['Minter address']

        jetton_table.field_names = field_names

        for minter in jetton_minters:
            jetton_wallets = jetton_wallet_map[minter.account.address]
            for jetton_wallet in jetton_wallets:
                ton_wallet = self.ctx.keystore.get_record_by_address(Address(jetton_wallet.owner_address))
                row = []
                if wallet is None:
                    row += [ton_wallet.name, Address(ton_wallet.address).to_mask()]
                if known_minters:
                    row += ['✓' if Address(minter.account.address) in known_minters else '']

                row += [minter.metadata.symbol or '',
                        minter.metadata.name or '',
                        jetton_wallet.balance_readable(minter.metadata)]
                row += [minter.account.address]
                jetton_table.add_row(row)
            if wallet is None:
                row = ['Total', '']
                if known_minters:
                    row += ['']
                row += ['', '', sum([jw.balance_readable(minter.metadata) for jw in jetton_wallets]), '']
                jetton_table.add_row(row)

        echo_success(jetton_table, only_msg=True)

    def __transfer_jetton(self, to_address: Address, record: Record, jetton_amount: decimal.Decimal,
                          jetton_wallet_info: JettonWalletResult, jetton_minter_info: JettonMinterResult,
                          wait_for_result: bool):
        wallet, _ = self.get_wallet_from_record(record)
        with processing():
            jetton_amount = int(jetton_amount * 10 ** jetton_minter_info.metadata.decimals)

            task_id = self.ctx.background_task_manager.jetton_transfer_task(
                jetton_minter_info=jetton_minter_info,
                from_wallet=wallet,
                from_jetton_wallet_addr=Address(
                    jetton_wallet_info.account.address),
                to_address=to_address,
                jetton_amount=jetton_amount,
                gas_amount=self.ctx.config.jetton.gas_amount
            )

        if not wait_for_result:
            echo_success("Transaction has been queued.")
            return

        self._wait_for_result_and_echo(task_id)

    @staticmethod
    def __menufy_jetton_minter(minter: JettonMinterResult,
                               symbol_max_len: int = 0,
                               known_minters: Tuple[Address] = tuple()):
        return ('{:<%d}  {} {}' % (symbol_max_len + 4)).format(
            (minter.metadata.symbol or '') + (' ✓' if Address(minter.account.address) in known_minters else ''),
            minter.metadata.name or '',
            f'[{Address(minter.account.address).to_mask()}]'
        )

    def __menufy_jetton_wallet(self, wallet: JettonWalletResult, minter: JettonMinterResult):
        owner_address = Address(wallet.owner_address)
        return '{} [{}] {}'.format(self.ctx.keystore.get_record_by_address(owner_address).name,
                                   owner_address.to_mask(),
                                   wallet.balance_readable(minter.metadata))


def _get_jetton_wallet_map(jetton_wallets):
    jetton_wallet_map = {}
    for wallet in jetton_wallets:
        if wallet.jetton_master_address not in jetton_wallet_map:
            jetton_wallet_map[wallet.jetton_master_address] = []
        jetton_wallet_map[wallet.jetton_master_address].append(wallet)
    for master_address, wallets in jetton_wallet_map.items():
        wallets.sort(key=lambda wallet: wallet.balance, reverse=True)
    return jetton_wallet_map


def _sorted_minters(jetton_minters):
    return sorted(jetton_minters, key=lambda minter: [minter.metadata.symbol is None, str(minter.metadata.symbol)])
