import itertools
import typing as t
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

import inquirer

from tons.tonclient.utils import Record, MultiSigOrderRecord, MultiSigWalletRecord
from tons.tonclient.utils._exceptions import MultiSigRecordAlreadyExistsError
from tons.tonsdk.contract import Contract
from tons.tonsdk.contract.wallet import MultiSigTransferRequest, get_multisig_order_address, MultiSigInfo, \
    MultiSigUpdateRequest
from tons.tonsdk.utils import Address, TonCurrencyEnum
from tons.ui._utils import SharedObject
from tons.ui.interactive_cli._modified_inquirer import ListWithFilter
from tons.ui.interactive_cli._sets._base import BaseSet, MenuItem
from tons.ui.interactive_cli._sets._mixin import KeyStoreMixin
from tons.ui.interactive_cli._sets._multisig._mixin import MultiSigMixin
from tons.ui.interactive_cli._sets._multisig._utils import add_menu_item
from tons.ui.interactive_cli._utils import processing, echo_error, echo_success
from tons.ui.interactive_cli._validators import number_greater_than_or_equal_to_zero, non_empty_string

_Timestamp = int
_Action = t.Union[MultiSigTransferRequest, MultiSigUpdateRequest]

class _Abort(Exception):
    pass


class MultiSigPlaceOrderSet(BaseSet, MultiSigMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick order type"

    def _handlers(self) -> t.OrderedDict[str, MenuItem]:
        ord_dict = OrderedDict()
        add_menu_item(ord_dict, "Transfer", "t", self._handle_transfer)
        add_menu_item(ord_dict, "Update params", "u", self._handle_update_params)
        add_menu_item(ord_dict, "Back", 'b', self._handle_exit)

        return ord_dict

    # ==================================================================================================================

    def _handle_transfer(self):
        self._handle_place_order(self._select_transfer_actions)

    def _select_transfer_actions(self, multisig: MultiSigWalletRecord) -> t.List[MultiSigTransferRequest]:
        receiver = self.select_contact("Select recipient")
        amount = self._prompt([inquirer.Text("amount", message='Amount in TON coins to transfer',
                                             validate=number_greater_than_or_equal_to_zero)])['amount']
        amount = Decimal(amount)
        message = self._prompt([inquirer.Text(
            "message", message='Message (press \'Enter\' to skip)', default=receiver.default_message), ])['message']

        body = Contract.text_message_to_cell(message) if message else None

        actions = [
            MultiSigTransferRequest.send_ton(
                amount=Decimal(amount),
                currency=TonCurrencyEnum.ton,
                src=multisig.address,
                dest=receiver.address,
                body=body
            )
        ]
        return actions

    # ==================================================================================================================

    def _handle_update_params(self):
        try:
            multisig, multisig_info, deployer, expiry = self._select_common_order_info()
        except _Abort:
            return
        actions = self._select_update_params_actions(multisig)
        self._save_and_place_order(actions, multisig, multisig_info, deployer, expiry)

    def _select_update_params_actions(self, _multisig: MultiSigWalletRecord) -> t.List[MultiSigUpdateRequest]:
        updated_config = self._select_multisig_config()
        actions = [
            MultiSigUpdateRequest(
                threshold=updated_config.threshold,
                signers=updated_config.signers,
                proposers=updated_config.proposers
            )
        ]
        return actions


    # ==================================================================================================================

    def _handle_place_order(self, select_actions: t.Callable[[MultiSigWalletRecord], t.List[_Action]]):
        try:
            multisig, multisig_info, deployer, expiry = self._select_common_order_info()
        except _Abort:
            return
        actions = select_actions(multisig)
        self._save_and_place_order(actions, multisig, multisig_info, deployer, expiry)

    def _default_order_name(self) -> str:
        now = datetime.utcnow()
        now = now.strftime("%y-%m-%d %H:%M:%S")
        return f"Order {now}"

    def _select_common_order_info(self) -> t.Tuple[MultiSigWalletRecord, MultiSigInfo, Record, _Timestamp]:
        multisig = self._select_multisig(verbose=True)
        if multisig is None:
            raise _Abort

        with processing():
            _, multisig_info = self.ctx.ton_client.get_multisig_information(multisig.address)

        def is_signer_or_proposer(record: Record):
            return Address(record.address) in itertools.chain(multisig_info.signers, multisig_info.proposers)

        deployer = self.select_wallet("Select deployer (signer or proposer)",
                                      verbose=True,
                                      filter_=is_signer_or_proposer,
                                      no_wallets_message='None of your keystore wallets is signer or proposer for this multisig')
        if deployer is None:
            raise _Abort
        deployer = self.ctx.keystore.get_record_by_name(deployer)

        expiry = self._get_expiry()

        return multisig, multisig_info, deployer, expiry

    def _save_and_place_order(self, actions: t.Sequence[_Action],
                              multisig: MultiSigWalletRecord, multisig_info: MultiSigInfo, deployer: Record,
                              expiry: _Timestamp):
        is_signer, address_idx = multisig_info.get_is_signer_and_address_idx(deployer.address)
        assert address_idx is not None
        order_id = multisig_info.get_next_order_seqno()

        self._save_deployed_order(multisig.address, order_id)
        wait_for_result = self._get_wait_for_result()
        from_wallet = self._get_deployer_wallet(deployer)

        with processing():
            task_id = self.ctx.background_task_manager.deploy_order_task(
                from_wallet,
                actions,
                expiry,
                is_signer,
                address_idx,
                order_id,
                multisig.address,
            )

        if not wait_for_result:
            echo_success('Task has been added to the queue.')
            return

        self._wait_for_result_and_echo(task_id)

    def _get_expiry(self) -> _Timestamp:
        time_delta_map: t.Dict[str, int] = {
            '1 hour': 3600,
            '1 day': 3600 * 24,
            '1 month': 3600 * 24 * 31,
            '3 months': 3600 * 24 * (31 + 30 + 31),
            '6 months': 3600 * 24 * 183,
            '1 year': 3600 * 24 * 366
        }

        choices, values = zip(*time_delta_map.items())
        key = 'expiration'
        questions = [
            ListWithFilter(
                key,
                message='Choose expiration time',
                choices=ListWithFilter.zip_choices_and_values(choices, values),
                carousel=True,
                default=time_delta_map['1 month']
            )
        ]
        time_delta: int = self._prompt(questions)[key]
        now = int(datetime.now().timestamp())
        return now + time_delta

    def _save_deployed_order(self, multisig_address: t.Union[Address, str], order_id: int):
        order_address = get_multisig_order_address(Address(multisig_address), order_id)
        order_address = order_address.to_string(True, True, True)
        while True:
            ans = self._prompt([
                inquirer.Text("name", message='Save as', validate=non_empty_string, default=self._default_order_name()),
                inquirer.Text("comment", message='Comment'),
            ])
            try:
                with self._multisig_order_list().restore_on_failure():
                    record = MultiSigOrderRecord(
                        address=order_address,
                        name=ans['name'],
                        comment=ans['comment']
                    )
                    self._multisig_order_list().add_record(record)
                    self._multisig_order_list().save()
            except MultiSigRecordAlreadyExistsError as exc:
                echo_error(str(exc))
                continue
            else:
                echo_success(f"Address {order_address} has been saved as {ans['name']}")
                break

