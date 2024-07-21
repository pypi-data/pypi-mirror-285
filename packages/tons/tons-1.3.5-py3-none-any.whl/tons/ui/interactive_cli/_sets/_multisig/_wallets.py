import typing as t
from collections import OrderedDict

import inquirer

from tons.tonclient._client._base import FailedToParseDataCell
from tons.tonclient.utils import Record, MultiSigWalletRecord
from tons.tonclient.utils._exceptions import MultiSigRecordAlreadyExistsError, MultiSigRecordDoesNotExistError
from tons.tonsdk.contract.wallet import MultiSigConfig, MultiSigWalletContractV2, WalletContract
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject, form_multisig_wallet_table, display_multisig_info, get_wallet_from_record_ctx, \
    echo_list_item_address
from tons.ui.interactive_cli._sets._base import BaseSet, MenuItem
from ._utils import add_menu_item
from .._mixin import KeyStoreMixin, keystore_sensitive_area
from ..._utils import echo_error, echo_success, processing, echo_warning
from ..._validators import integer_greater_than_zero, integer_greater_or_equal_than_zero, non_empty_string, \
    valid_address
from ._mixin import MultiSigMixin, InvalidMultisigConfig


class _Abort(Exception):
    pass

class MultiSigWalletSet(BaseSet, MultiSigMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick multisig wallet command [{self.ctx.keystore.name}]"

    def _handlers(self) -> t.OrderedDict[str, MenuItem]:
        ord_dict = OrderedDict()
        add_menu_item(ord_dict, "List", "l", self._handle_list)
        add_menu_item(ord_dict, "Get", "g", self._handle_get)
        add_menu_item(ord_dict, "Create and deploy", "c", self._handle_deploy)
        add_menu_item(ord_dict, "Import", "i", self._handle_import)
        add_menu_item(ord_dict, "Edit", "e", self._handle_edit)
        add_menu_item(ord_dict, "Delete", None, self._handle_delete)
        add_menu_item(ord_dict, "Back", 'b', self._handle_exit)

        return ord_dict

# +=================================================================================================================== #

    def _handle_list(self):
        records = self._multisig_wallet_list().get_records()
        addresses = [r.address for r in records]
        with processing():
            addresses_info, multisigs_info = self.ctx.ton_client.get_multisigs_information(addresses)
        t = form_multisig_wallet_table(records, multisigs_info, addresses_info)
        echo_success(str(t), only_msg=True)

# +=================================================================================================================== #

    def _handle_get(self):
        multisig = self._select_multisig()
        if multisig is None:
            return
        try:
            with processing():
                address_info, multisig_info = self.ctx.ton_client.get_multisig_information(multisig.address)
        except FailedToParseDataCell as exc:
            echo_error(str(exc))
            return

        display_multisig_info(address_info, multisig_info, self._find_extra_info_about_address)

# +=================================================================================================================== #

    def _handle_delete(self):
        multisig = self._select_multisig()
        if multisig is None:
            return
        if not self._is_sure(f"Are you sure you want to delete this multisig? This cannot be undone."):
            echo_success("Action canceled.")
            return

        with self._multisig_wallet_list().restore_on_failure():
            self._multisig_wallet_list().delete_record(record=multisig)
            self._multisig_wallet_list().save()

        echo_success("Multisig deleted.")

# +=================================================================================================================== #

    def _handle_edit(self):
        multisig = self._select_multisig()
        if multisig is None:
            return

        ans = self._prompt([
            inquirer.Text("address", message='Address', validate=valid_address, default=multisig.address),
            inquirer.Text("name", message='Name', validate=non_empty_string, default=multisig.name),
            inquirer.Text("comment", message='Comment', default=multisig.comment),
        ])

        try:
            with self._multisig_wallet_list().restore_on_failure():
                self._multisig_wallet_list().edit_record(multisig.name,
                                                         new_name=ans['name'],
                                                         new_address=ans['address'],
                                                         new_comment=ans['comment'])
                self._multisig_wallet_list().save()
        except MultiSigRecordAlreadyExistsError as exc:
            echo_error(str(exc))
            return

        echo_success("Multisig edited.")



# +=================================================================================================================== #

    def _handle_import(self):
        questions = [
            inquirer.Text("address", message='Enter the address', validate=valid_address),
            inquirer.Text("name", message='Enter the name', validate=non_empty_string),
            inquirer.Text("comment", message='Enter the comment'),
        ]
        ans = self._prompt(questions)

        address = ans["address"].strip()
        name = ans["name"]
        comment = ans["comment"]

        try:
            with processing():
                self.ctx.ton_client.get_multisig_information(address)
        except FailedToParseDataCell:
            if not self._is_sure("Failed to get or parse data cell. This might not be a proper multisig wallet. Import anyway?"):
                echo_success("Action canceled.")
                return

        record = MultiSigWalletRecord(
            name=name,
            address=address,
            comment=comment
        )

        try:
            with self._multisig_wallet_list().restore_on_failure():
                self._multisig_wallet_list().add_record(record)
                self._multisig_wallet_list().save()
        except MultiSigRecordAlreadyExistsError as exc:
            echo_error(str(exc))
            return

        echo_success("Multisig imported.")



# +=================================================================================================================== #

    def _handle_deploy(self):
        try:
            deployer = self._select_deployer()
            config = self._select_multisig_config()
            contract = MultiSigWalletContractV2(config=config)

            address_already_saved = self._check_address_already_saved(contract)
            if not address_already_saved:
                self._save_deployed_multisig(contract.address)

            wait_for_result = self._get_wait_for_result()
            deployer_wallet = self._get_deployer_wallet(deployer)

            with processing():
                task_id = self.ctx.background_task_manager.deploy_multisig_task(deployer_wallet, contract)

            if not wait_for_result:
                echo_success('Task has been added to the queue.')
                return

            self._wait_for_result_and_echo(task_id)

        except InvalidMultisigConfig as exc:
            echo_error(str(exc))

        except _Abort:
            return

    def _check_address_already_saved(self, contract: MultiSigWalletContractV2) -> bool:
        address = Address(contract.address)
        try:
            record = self._multisig_wallet_list().get_record(address=address)
        except MultiSigRecordDoesNotExistError:
            return False
        else:
            echo_warning(f'Multisig with these parameters is already saved as {record.name}')
            if not self._is_sure("Do you still want to send a deployment message?"):
                echo_success("Aborted.")
                raise _Abort
            return True

    def _save_deployed_multisig(self, multisig_address: t.Union[Address, str]):
        multisig_address = Address(multisig_address).to_string(True, True, True)
        while True:
            ans = self._prompt([
                inquirer.Text("name", message='Save as', validate=non_empty_string),
                inquirer.Text("comment", message='Comment'),
            ])
            try:
                with self._multisig_wallet_list().restore_on_failure():
                    record = MultiSigWalletRecord(
                        address=multisig_address,
                        name=ans['name'],
                        comment=ans['comment']
                    )
                    self._multisig_wallet_list().add_record(record)
                    self._multisig_wallet_list().save()
            except MultiSigRecordAlreadyExistsError as exc:
                echo_error(str(exc))
                continue
            else:
                echo_success(f"Address {multisig_address} has been saved as {ans['name']}")
                break

    def _select_deployer(self) -> t.Optional[Record]:
        deployer_name = self.select_wallet("Select deployer", True)
        if deployer_name is None:
            raise _Abort
        return self.ctx.keystore.get_record_by_name(deployer_name)


# +=================================================================================================================== #



