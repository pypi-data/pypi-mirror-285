import typing as t
from collections import OrderedDict

import inquirer

from tons.tonclient._client._base import FailedToParseDataCell
from tons.tonclient.utils import Record, MultiSigOrderRecord
from tons.tonclient.utils._exceptions import MultiSigRecordAlreadyExistsError
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject, display_order_info
from ._new_order import MultiSigPlaceOrderSet
from ._order_list import OrderListSet
from ._order_select import select_order_with_relevance
from .._base import BaseSet, MenuItem
from ._mixin import MultiSigMixin
from ._utils import add_menu_item
from ..._utils import processing, echo_success, echo_error
from ..._validators import valid_address, non_empty_string


class _Abort(Exception):
    pass


class MultiSigOrderSet(BaseSet, MultiSigMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick order command [{self.ctx.keystore.name}]"

    def _handlers(self) -> t.OrderedDict[str, MenuItem]:
        ord_dict = OrderedDict()
        add_menu_item(ord_dict, "List", "l", self._handle_list)
        add_menu_item(ord_dict, "Get", "g", self._handle_get)
        add_menu_item(ord_dict, "Place new", "p", self._handle_deploy)
        add_menu_item(ord_dict, "Approve", "a", self._handle_approve)
        add_menu_item(ord_dict, "Import", "i", self._handle_import)
        add_menu_item(ord_dict, "Edit", "e", self._handle_edit)
        add_menu_item(ord_dict, "Delete", None, self._handle_delete)
        # add_menu_item(ord_dict, "Delete all expired & executed", "x", self._handle_cleanup)
        add_menu_item(ord_dict, "Back", 'b', self._handle_exit)

        return ord_dict

    # +=================================================================================================================== #

    def _handle_list(self):
        OrderListSet(self.ctx).show()

    # +=================================================================================================================== #

    def _handle_get(self):
        order = select_order_with_relevance(self.ctx, 'Get from')
        if order is None:
            return

        try:
            with processing():
                address_info, order_info = self.ctx.ton_client.get_multisig_order_information(order.address)
        except FailedToParseDataCell as exc:
            echo_error(str(exc))
        else:
            display_order_info(address_info, order_info, self._find_extra_info_about_address)

    # +=================================================================================================================== #

    def _handle_delete(self):
        order = select_order_with_relevance(self.ctx, "Delete from")
        if order is None:
            return
        if not self._is_sure(f"Are you sure you want to delete this order? This cannot be undone."):
            echo_success("Action canceled.")
            return

        with self._multisig_order_list().restore_on_failure():
            self._multisig_order_list().delete_record(record=order)
            self._multisig_order_list().save()

        echo_success("Order deleted.")

    # +=================================================================================================================== #

    def _handle_edit(self):
        order = select_order_with_relevance(self.ctx, "Edit from")
        if order is None:
            return
        ans = self._prompt([
            inquirer.Text("address", message='Address', validate=valid_address, default=order.address),
            inquirer.Text("name", message='Name', validate=non_empty_string, default=order.name),
            inquirer.Text("comment", message='Comment', default=order.comment),
        ])

        try:
            with self._multisig_order_list().restore_on_failure():
                self._multisig_order_list().edit_record(order.name,
                                                         new_name=ans['name'],
                                                         new_address=ans['address'],
                                                         new_comment=ans['comment'])
                self._multisig_order_list().save()
        except MultiSigRecordAlreadyExistsError as exc:
            echo_error(str(exc))
            return

        echo_success("Order edited.")

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
                addr_info, order_info = self.ctx.ton_client.get_multisig_order_information(address)
        except FailedToParseDataCell:
            if not self._is_sure(
                        "Failed to get or parse data cell. This might not be a proper multisig order. Import anyway?"):
                echo_success("Action canceled.")
                return

        else:
            if order_info.actions is None:
                if not self._is_sure(
                    "Failed to parse order actions. IT IS NOT RECOMMENDED TO SIGN THIS ORDER. Import anyway?"
                ):
                    echo_success("Action cancelled.")
                    return

        record = MultiSigOrderRecord(
            name=name,
            address=address,
            comment=comment
        )
        try:
            with self._multisig_order_list().restore_on_failure():
                self._multisig_order_list().add_record(record)
                self._multisig_order_list().save()
        except MultiSigRecordAlreadyExistsError as exc:
            echo_error(str(exc))
            return

        echo_success("Multisig imported.")

    # +=================================================================================================================== #

    def _handle_deploy(self):
        MultiSigPlaceOrderSet(self.ctx).show()

    # +=================================================================================================================== #

    def _handle_approve(self):
        order = self._select_active_order()
        if order is None:
            return

        try:
            with processing():
                address_info, order_info = self.ctx.ton_client.get_multisig_order_information(order.address)
        except FailedToParseDataCell as exc:
            echo_error(str(exc))
            return

        if order_info.expired():
            echo_error("Order has expired.")
            return

        if order_info.executed:
            echo_error("Order has already been executed.")
            return

        display_order_info(address_info, order_info, self._find_extra_info_about_address)
        if not self._is_sure("Please carefully review the order above. Are you sure you want to approve it?"):
            echo_success("Aborted")
            return

        def is_signer(record: Record):
            return Address(record.address) in order_info.signers

        deployer = self.select_wallet("Select signer",
                                      verbose=True,
                                      filter_=is_signer,
                                      no_wallets_message='None of your keystore wallets is a signer for this multisig')
        if deployer is None:
            return

        deployer = self.ctx.keystore.get_record_by_name(deployer)

        signer_idx = order_info.signers.index(deployer.address)
        if order_info.approved_by(signer_idx):
            echo_success("The order is already approved by this signer.")
            return

        wait_for_result = self._get_wait_for_result()
        from_wallet = self._get_deployer_wallet(deployer)

        with processing():
            task_id = self.ctx.background_task_manager.approve_order_task(
                from_wallet,
                order_info.signers.index(deployer.address),
                order.address
            )

        if not wait_for_result:
            echo_success('Task has been added to the queue.')
            return

        self._wait_for_result_and_echo(task_id)

    # +=================================================================================================================== #

    def _select_active_order(self) -> t.Optional[MultiSigOrderRecord]:
        return self._select_order(True, 'active order', self._order_relevance_getter())

    def _select_inactive_order(self) -> t.Optional[MultiSigOrderRecord]:
        return self._select_order(True, 'order from history', self._order_irrelevance_getter(),
                                  'Your order history is empty.')
