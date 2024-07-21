from collections import OrderedDict
from datetime import datetime
from typing import Dict, Tuple, Sequence, List, Iterator, Set
from typing import Optional
from typing import OrderedDict as OrderedDictTyping
from uuid import UUID

from colorama import Fore

from tons.tonclient._client._base import NftItemInfoResult
from tons.tonsdk.contract.wallet import Wallets
from tons.tonsdk.utils import InvalidAddressError, Address
from ._base import BaseSet, MenuItem
from ._mixin import KeyStoreMixin, keystore_sensitive_area
from .._modified_inquirer import terminal, ListWithFilter, ModifiedConfirm
from .._utils import echo_success, echo_error, processing

from .._background import DNSRefreshBackgroundTask
from ..._utils import SharedObject, form_dns_table, dns_expires_soon, shorten_dns_domain, batches


class DNSSet(BaseSet, KeyStoreMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick DNS command [{self.ctx.keystore.name}]"

    def _handlers(self) -> OrderedDictTyping[str, MenuItem]:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}R{terminal.no_underline}efresh ownership"] = \
            MenuItem(self._handle_refresh_ownership, "r")
        ord_dict[f"{terminal.underline}L{terminal.no_underline}ist DNS"] = \
            MenuItem(self._handle_show_dns, "l")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_refresh_ownership(self) -> None:
        with processing():
            addresses = [record.address for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)]
            dns_items_info = self.ctx.ton_client.get_dns_items_information(addresses)

        if len(dns_items_info) == 0:
            echo_success("You do not have any domains.", only_msg=True)
            return

        choices = ['(all expiring sooner than in %d months)' % self.ctx.config.dns.max_expiring_in] + \
                  [self.__menufy_dns_info(item) for item in dns_items_info]
        values = [None] + dns_items_info

        questions = [
            ListWithFilter(
                "domain",
                message="Select domain to refresh",
                choices=ListWithFilter.zip_choices_and_values(choices, values),
                carousel=True
            ),
            ModifiedConfirm(
                "wait_for_result", message="Wait until transaction will be completed?", default=True),
        ]
        ans = self._prompt(questions)
        if ans['domain'] is None:
            items_to_refresh = [item for item in dns_items_info
                                if dns_expires_soon(item, self.ctx.config.dns.max_expiring_in)]
        else:
            items_to_refresh = [ans['domain']]

        self._refresh_ownership(items_to_refresh, ans["wait_for_result"])

    def _handle_show_dns(self):
        with processing():
            addresses = [record.address for record in self.ctx.keystore.get_records(self.ctx.config.tons.sort_keystore)]
            dns_items_info = self.ctx.ton_client.get_dns_items_information(addresses)
        echo_success(str(form_dns_table(dns_items_info)), only_msg=True)

    def __menufy_dns_info(self, dns_item) -> str:
        dns_domain = shorten_dns_domain(dns_item.dns_domain) + '.ton'
        try:
            mask = Address(dns_item.account.address).to_mask()
        except InvalidAddressError:
            mask = 'NA'
        try:
            expires_datetime = datetime.utcfromtimestamp(int(dns_item.dns_expires))
        except TypeError:
            expires = 'NA'
        else:
            expires = expires_datetime.strftime('%Y-%m-%d %H:%M:%S')
            if dns_expires_soon(dns_item, self.ctx.config.dns.max_expiring_in):
                expires = Fore.RED + expires + Fore.RESET

        return '{:<30} [{}  expires: {} UTC]'.format(dns_domain, mask, expires)

    def _refresh_ownership(self, dns_items: Sequence[NftItemInfoResult], wait_for_result: bool):
        if len(dns_items) == 0:
            echo_success('No domain needs to update ownership.')
            return
        self.__refresh_ownership(dns_items, wait_for_result)

    @keystore_sensitive_area
    def __refresh_ownership(self, dns_items: Sequence[NftItemInfoResult], wait_for_result: bool):
        pending_tasks: Set[UUID] = set()

        dns_address_map = self.__get_dns_address_map(dns_items)

        for raw_address, address_dns_items in dns_address_map.items():
            record = self.ctx.keystore.get_record_by_address(Address(raw_address))
            with processing():
                wallet, _ = self.ctx.keystore.get_wallet_from_record(record)
                for dns_item_batch in self.__dns_batches(address_dns_items):
                    task_id = self.ctx.background_task_manager.dns_refresh_task(from_wallet=wallet,
                                                                                dns_items=dns_item_batch)
                    pending_tasks.add(task_id)

        if not wait_for_result:
            echo_success("Transactions have been queued.")
            return

        while len(pending_tasks) > 0:
            with processing():
                task_id, task = self.__get_next_finished_task(pending_tasks)
            _echo = echo_success if not task.result_is_bad else lambda msg: echo_error(msg, only_cross=True)

            for idx, dns_item in enumerate(task.dns_items):
                if isinstance(task.result_description, str):
                    result_description = task.result_description
                else:
                    result_description = task.result_description[idx]

                _echo(f"{shorten_dns_domain(dns_item.dns_domain)}.ton: {result_description}. "
                      f"Wallet address: {dns_item.owner_or_max_bidder}")

            pending_tasks.remove(task_id)

    @classmethod
    def __dns_batches(cls, dns_items: List[NftItemInfoResult], batch_size: int = 4) -> Iterator[List[NftItemInfoResult]]:
        yield from batches(dns_items, batch_size)

    def __get_dns_address_map(self, dns_items: Sequence[NftItemInfoResult]) -> Dict[str, List[NftItemInfoResult]]:
        dns_address_map: Dict[str, List[NftItemInfoResult]] = dict()
        for dns_item in dns_items:
            try:
                raw_address = Address.raw_id(dns_item.owner_or_max_bidder)
            except InvalidAddressError:
                echo_error(f"{shorten_dns_domain(dns_item.dns_domain)}.ton: Invalid NFT data.")
                continue
            try:
                dns_address_map[raw_address].append(dns_item)
            except KeyError:
                dns_address_map[raw_address] = [dns_item]
        return dns_address_map

    def __get_next_finished_task(self, pending_tasks: Set[UUID]) -> \
            Tuple[UUID, DNSRefreshBackgroundTask]:
        while True:
            for task_id in pending_tasks:
                if not (task := self.ctx.background_task_manager.get_task(task_id)).is_pending:
                    assert isinstance(task, DNSRefreshBackgroundTask)
                    return task_id, task
