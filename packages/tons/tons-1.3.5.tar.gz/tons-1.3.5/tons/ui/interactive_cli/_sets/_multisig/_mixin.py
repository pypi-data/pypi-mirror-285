import typing as t

import inquirer

from tons.tonclient.utils import LocalMultiSigWalletList, MultiSigWalletRecord, LocalMultiSigOrderList, \
    MultiSigOrderRecord, WhitelistContact, WhitelistContactType, Record
from tons.tonclient.utils._exceptions import MultiSigRecordDoesNotExistError
from tons.tonclient.utils._multisig import BaseMultiSigRecordList, BaseMultiSigRecord
from tons.tonsdk.contract.wallet import WalletContract, MultiSigConfig, MultiSigOrderData
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject, get_wallet_from_record_ctx, find_extra_info_about_address
from .._mixin import keystore_sensitive_area, KeyStoreMixin
from ..._utils import echo_success, processing, echo_error
from tons.ui.interactive_cli._modified_inquirer import ListWithFilter, ModifiedConfirm
from ..._validators import integer_greater_than_zero, integer_greater_or_equal_than_zero


class InvalidMultisigConfig(Exception):
    pass


MultiSigRecordFilter = t.Callable[[BaseMultiSigRecord], bool]


class MultiSigMixin(KeyStoreMixin):
    ctx: SharedObject

    def _multisig_wallet_list(self) -> LocalMultiSigWalletList:
        return self.ctx.keystore.multisig_wallet_list

    def _multisig_order_list(self) -> LocalMultiSigOrderList:
        return self.ctx.keystore.multisig_order_list

    def _select_multisig(self, verbose: bool = False) -> t.Optional[MultiSigWalletRecord]:
        return self._select_multisig_entity(self._multisig_wallet_list(), 'multisig', verbose)

    def _select_order(self, verbose: bool = False,
                      entity_name: str = 'order',
                      filter_: t.Optional[MultiSigRecordFilter] = None,
                      empty_list_message: t.Optional[str] = None) -> t.Optional[MultiSigOrderRecord]:
        return self._select_multisig_entity(self._multisig_order_list(), entity_name, verbose, filter_, empty_list_message)

    def _select_multisig_entity(self,
                                list_: BaseMultiSigRecordList,
                                entity_name: str,
                                verbose: bool = False,
                                filter_: t.Optional[MultiSigRecordFilter] = None,
                                empty_list_message: t.Optional[str] = None
                                ) -> t.Optional[BaseMultiSigRecord]:
        entities = list_.get_records()
        if filter_ is not None:
            entities = tuple(filter(filter_, entities))

        if not entities:
            if empty_list_message is None:
                empty_list_message = f"You do not have any {entity_name}s yet."
            echo_success(empty_list_message)
            return

        choices = [m.pretty_string() for m in entities]

        if verbose:
            with processing():
                addresses = [e.address for e in entities]
                address_infos = self.ctx.ton_client.get_addresses_information(addresses)

            for idx, address_info in enumerate(address_infos):
                choices[idx] = KeyStoreMixin.add_mask_and_balance(
                    choices[idx],
                    Address(address_info.address).to_mask(),
                    address_info.balance
                )

        values = list(entities)

        key = "wallet"
        return self._prompt([
            ListWithFilter(
                key,
                message=f"Select {entity_name}",
                choices=ListWithFilter.zip_choices_and_values(choices,
                                                              values),
                carousel=True,
            )
        ])[key]

    def _is_sure(self, message: str) -> bool:
        is_sure = self._prompt([
            ModifiedConfirm(
                "is_sure", message=message,
                default=False),
        ])["is_sure"]
        return bool(is_sure)

    def _find_extra_info_about_address(self, addr: t.Union[str, Address]) -> str:
        return find_extra_info_about_address(self.ctx, addr)

    def _get_wait_for_result(self) -> bool:
        key = "wait_for_result"
        questions = [ModifiedConfirm(key, message="Wait until transaction will be completed?",
                                     default=True)]
        return self._prompt(questions)[key]

    @keystore_sensitive_area
    def _get_deployer_wallet(self, deployer: Record) -> WalletContract:
        return get_wallet_from_record_ctx(self.ctx, deployer)

    def _select_multisig_config(self) -> MultiSigConfig:
        signers = self._select_signers()
        proposers = self._select_proposers()
        threshold = self._select_threshold(default=len(signers))
        allow_arbitrary_seqno = True

        try:
            return MultiSigConfig(
                signers=signers,
                proposers=proposers,
                threshold=threshold,
                allow_arbitrary_seqno=allow_arbitrary_seqno
            )
        except ValueError as exc:
            raise InvalidMultisigConfig(str(exc))

    def _select_threshold(self, default: int) -> int:
        key = "threshold"
        questions = [
            inquirer.Text(key,
                          message="Threshold",
                          validate=integer_greater_than_zero,
                          default=default)
        ]
        return int(self._prompt(questions)[key])

    def _select_signers_num(self) -> int:
        key = "signers_num"
        questions = [
            inquirer.Text(key,
                          message="Number of signers",
                          validate=integer_greater_than_zero,
                          default=2)
        ]
        return int(self._prompt(questions)[key])

    def _select_signers(self) -> t.List[Address]:
        signers_num = self._select_signers_num()
        return self._select_members(signers_num, 'signer')

    def _select_proposers_num(self) -> int:
        key = "proposers_num"
        questions = [
            inquirer.Text(key,
                          message="Number of proposers",
                          validate=integer_greater_or_equal_than_zero,
                          default="0")
        ]
        return int(self._prompt(questions)[key])

    def _select_proposers(self) -> t.List[Address]:
        proposers_num = self._select_proposers_num()
        return self._select_members(proposers_num, 'proposer')

    def _select_members(self, members_num: int, member_type: str) -> t.List[Address]:
        members = []
        for idx in range(members_num):
            while True:
                member = self.select_contact(f"Select {member_type} #{idx}",
                                             show_balance=True)
                member = Address(member.address)
                if member in members:
                    echo_error(f'This {member_type} is already selected.')
                    continue
                members.append(member)
                break
        return members

    # +=================================================================================================================== #

    def _order_relevance_getter(self) -> MultiSigRecordFilter:
        addresses = [Address.raw_id(o.address) for o in self._multisig_order_list().get_records()]
        with processing():
            _, orders_info = self.ctx.ton_client.get_multisig_orders_information(addresses)

        actuality_matrix: t.Dict[str, bool] = dict()
        for address, order_info in zip(addresses, orders_info):
            if order_info is None:
                continue
            assert isinstance(order_info, MultiSigOrderData)
            actuality_matrix[address] = not (order_info.expired() or order_info.executed)

        def is_relevant(order: BaseMultiSigRecord) -> bool:
            return actuality_matrix.get(Address.raw_id(order.address), False)

        return is_relevant

    def _order_irrelevance_getter(self) -> MultiSigRecordFilter:
        is_relevant = self._order_relevance_getter()

        def is_irrelevant(order: BaseMultiSigRecord) -> bool:
            return not is_relevant(order)

        return is_irrelevant

    def _select_active_order(self) -> t.Optional[MultiSigOrderRecord]:
        return self._select_order(True, 'active order', self._order_relevance_getter())

    def _select_inactive_order(self) -> t.Optional[MultiSigOrderRecord]:
        return self._select_order(True, 'order from history', self._order_irrelevance_getter(),
                                  'Your history is empty.')
