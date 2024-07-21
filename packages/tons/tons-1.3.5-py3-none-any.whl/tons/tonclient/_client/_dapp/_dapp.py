import decimal
import math
from datetime import datetime
from time import sleep, time

from typing import List, Union, Optional, Tuple, Dict, Callable, Sequence

from tons import settings
from tons.config import Config
from tons.logging_ import tons_logger
from tons.tonsdk.boc import Cell
from tons.tonsdk.contract.token.ft import JettonWallet
from tons.tonsdk.contract.wallet import SendModeEnum, WalletContract, InternalMessage, MultiSigWalletContractV2, \
    MultiSigInfo, MultiSigOrderData, MultiSigTransferRequest, MultiSigUpdateRequest, new_multisig_order_body, \
    pack_multisig_order_approve
from tons.tonsdk.provider.dapp import DAppClient, DAppWrongResult, BroadcastQuery
from tons.tonsdk.utils import TonCurrencyEnum, from_nano, Address, b64str_to_bytes, \
    bytes_to_b64str, to_nano
from ._queries import Accounts, Comparison, DAppGqlIdOrderedQuery, NftItems, JettonWallets, JettonMinters, raw_ids, \
    Price, \
    Transactions, Blocks, DAppGqlQuery, Info
from .._base import (TonClient, AddressInfoResult, BroadcastResult, BroadcastStatusEnum, NftItemInfoResult, \
    JettonWalletResult, JettonMinterResult, AddressState, TransactionInfo, TransactionHashNotFound, BlockInfo,
                     InfoInfo, FailedToParseDataCell)
from ..._exceptions import TonDappError, TON_EXCEPTION_BY_CODE, TonError


class SpecialTonDappError(TonDappError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, code=None)

    def __str__(self):
        return self.detail


class InsufficientBalanceError(SpecialTonDappError):
    def __init__(self):
        super().__init__("insufficient balance")


class TransactionNotFound(SpecialTonDappError):
    def __init__(self):
        super().__init__("transaction has been not confirmed, its status is unknown")


class TransactionNotCommitted(SpecialTonDappError):
    def __init__(self):
        super().__init__("transaction has not been committed to the blockchain")


class DAppTonClient(TonClient):
    TRY_AGAIN_SLEEP_SEC = 5
    TRANSACTION_TIMEOUT = 60
    BROADCAST_TIMEOUT = 0
    REQUEST_TIMEOUT = 60

    def __init__(self, config: Config):
        self.config = config
        self._provider: DAppClient = None

    @property
    def provider(self) -> DAppClient:
        if self._provider is None:
            self._provider = DAppClient(graphql_url=self.config.provider.dapp.graphql_url,
                                        broadcast_url=self.config.provider.dapp.broadcast_url,
                                        websocket_url=self.config.provider.dapp.websocket_url,
                                        api_key=self.config.provider.dapp.api_key)

        return self._provider

    def get_ton_price_usd(self) -> Optional[decimal.Decimal]:
        result = self._run_gql_query(Price())
        try:
            price = decimal.Decimal(result['usd']).quantize(decimal.Decimal('0.01'))
        except (decimal.InvalidOperation, TypeError, KeyError):
            return None

        return price

    def get_transaction_information(self, transaction_hash: str, raise_none: bool = False) -> Optional[TransactionInfo]:
        tons_logger().debug(f'get tx info')
        query = Transactions.by_id(transaction_hash)
        res = self._run_gql_query(query)
        try:
            res = res[0]
        except IndexError:
            if raise_none:
                raise TonDappError(f"Failed to get transaction information: tx_hash={transaction_hash}")
            return None
        return TransactionInfo(**res)

    def get_transaction_information_by_in_msg(self, in_msg: str) -> Optional[TransactionInfo]:
        query = Transactions.by_in_msg(in_msg)
        res = self._run_gql_query(query)
        try:
            res = res[0]
        except IndexError:
            return None
        return TransactionInfo(**res)

    def get_info(self) -> InfoInfo:
        query = Info()
        res = self._run_gql_query(query)
        return InfoInfo(**res)

    def get_time(self) -> float:
        try:
            backend_time = self.get_info().timestamp()
            system_time = time()
            return backend_time or system_time
        except:
            return time()

    def get_address_information(self, address: str,
                                currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) -> Optional[AddressInfoResult]:
        return self.get_addresses_information([address], currency_to_show)[0]

    def get_addresses_information(self, addresses: List[str],
                                  currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) -> \
            List[Optional[AddressInfoResult]]:
        tons_logger().debug(f'get addr info (n={len(addresses)})')
        if not addresses:
            return []

        address_ids = raw_ids(addresses)
        queries = [Accounts.by_ids(address_ids[i:i + settings.DAPP_RECORDS_LIMIT]).gql()
                   for i in range(0, len(address_ids), settings.DAPP_RECORDS_LIMIT)]
        results = self._run(lambda: self.provider.query(queries), single_query=False)
        accounts = []
        for result in results:
            accounts += result['accounts']

        address_infos = [None] * len(address_ids)
        for account in accounts:
            for idx, address_id in enumerate(address_ids):
                if address_id == account['id']:
                    address_infos[idx] = self._parse_addr_info(account, currency_to_show)
        for i in range(len(address_infos)):
            if address_infos[i] is None:
                address_infos[i] = AddressInfoResult(address=addresses[i], state=AddressState.uninit, balance=0)

        tons_logger().debug(f'got addr info ({len(accounts)}/{len(address_infos)})')
        return address_infos

    def get_dns_items_information(self, holders: List[Union[Address, str]], include_max_bid: bool = True) \
            -> List[NftItemInfoResult]:
        """
        Retrieve DNS items information for the specified holders.

        Args:
            holders (List[Union[Address, str]]): A list of holders (addresses or address strings)
                to retrieve DNS items information for.
            include_max_bid (bool, optional): Determines whether to include DNS items where the holders
                are the maximum bidders in finished auctions, but did not claim ownership. Defaults to True.

        Returns:
            List[NftItemInfoResult]: A list of NftItemInfoResult objects containing DNS items information.

        Note:
            - The function retrieves DNS items information for the specified holders.
            - If `include_max_bid` is True, DNS items where the holders are the maximum bidders in finished auctions,
              but have not yet claimed their ownership, will also be included in the returned list.
            - The function uses pagination to retrieve the results in batches.
            - If no holders are provided, an empty list is returned.
        """
        tons_logger().debug(f'get dns info (holders={len(holders)}, include_max_bid={int(include_max_bid)})')
        if not holders:
            return []
        result = []

        query = NftItems.DNS(self.config.provider.dapp.dns_collection_address)
        query.filter.add(Comparison.owner_address_in(holders))
        result += [NftItemInfoResult(**r) for r in self._paginate(query)]
        if include_max_bid:
            query = NftItems.DNS(self.config.provider.dapp.dns_collection_address)
            query.filter.add(Comparison.dns_max_bidder_in(holders))
            query.filter.add(Comparison.dns_auction_finished())
            result += [NftItemInfoResult(**r) for r in self._paginate(query)]

        return result

    def form_dns_items_query(self, holders: List[Union[Address, str]], time_: int) -> Optional[NftItems]:
        if not holders:
            return None

        query = NftItems.DNS(self.config.provider.dapp.dns_collection_address)
        query.filter.add(Comparison.owner_address_in(holders))
        query.filter.add(Comparison.or_dns(holders, time_, self.config.provider.dapp.dns_collection_address))
        return query

    def get_paginated_dns_items_information(self, query: NftItems, page: Optional[str] = None) \
            -> Tuple[Optional[str], List[NftItemInfoResult]]:
        tons_logger().debug(f'get paginated dns info (query={query}')

        query.add_dns_pagination(page)
        results = self._run_gql_query(query)
        try:
            page = results[-1]['id']
        except IndexError:
            page = None

        return page, [NftItemInfoResult(**r) for r in results]

    def get_dns_domain_information(self, dns_domain: str, raise_none: bool = True) -> Optional[NftItemInfoResult]:
        tons_logger().debug(f'get dns domain info')
        query = NftItems.DNS(self.config.provider.dapp.dns_collection_address)
        query.filter.add(Comparison.dns_domain(dns_domain), behavior='replace')
        result = self._run_gql_query(query)
        try:
            result = result[0]
        except IndexError:
            if raise_none:
                raise TonDappError(f"Failed to retrieve dns info: {dns_domain}.ton")
            return None

        return NftItemInfoResult(**result)

    def get_jetton_information(self, owners: List[Union[Address, str]]) \
            -> Tuple[List[JettonMinterResult], List[JettonWalletResult]]:
        tons_logger().debug(f'get jetton info (owners={len(owners)})')

        if not owners:
            return [], []

        wallets_query = JettonWallets()
        wallets_query.filter.add(Comparison.owner_address_in(owners))
        jetton_wallets = [JettonWalletResult(**r) for r in self._paginate(wallets_query)]

        if len(jetton_wallets) == 0:
            return [], []

        minters_query = JettonMinters()
        minters_query.filter.add(Comparison.address_in([item.jetton_master_address for item in jetton_wallets]))
        jetton_minters = [JettonMinterResult(**r) for r in self._paginate(minters_query)]

        return jetton_minters, jetton_wallets

    def get_jetton_wallet(self, owner: Union[Address, str], minter_address: Union[Address, str],
                          raise_none: bool = True) -> Optional[JettonWalletResult]:
        tons_logger().debug(f'get jetton wallet')
        query = JettonWallets()
        query.filter.add(Comparison.owner_address(owner))
        query.filter.add(Comparison.jetton_master_address(minter_address))
        result = self._run_gql_query(query)
        try:
            result = result[0]
        except IndexError:
            if raise_none:
                raise TonDappError(f"Failed to retrieve jetton wallet info: owner={owner} minter={minter_address}")
            return None

        return JettonWalletResult(**result)

    def get_last_masterchain_block_info(self, raise_none: bool = False) -> Optional[BlockInfo]:
        query = Blocks.latest_masterchain_block()
        res = self._run_gql_query(query)
        try:
            res = res[0]
        except IndexError:
            if raise_none:
                raise TonDappError("Failed to get masterchain block info")
            return None

        return BlockInfo(**res)

    def get_multisig_information(self, addr: Union[Address, str],
                                 ton_currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) \
            -> Tuple[AddressInfoResult, MultiSigInfo]:
        """
        :raises: FailedToParseDataCell
        """
        tons_logger().debug(f'get multisig info {addr}')
        addr_info = self.get_address_information(Address(addr).to_string(), ton_currency_to_show)
        multisig_info = self._parse_multisig_wallet_data_cell(addr_info)
        return addr_info, multisig_info

    def get_multisigs_information(self, addresses: Sequence[Union[Address, str]],
                                  ton_currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) \
            -> [List[AddressInfoResult], List[Optional[MultiSigInfo]]]:
        """
        If fails to parse data cell, puts a None in the MultiSigInfo list
        """
        tons_logger().debug(f'get multisigs info {len(addresses)}')
        addresses = [Address(addr).to_string() for addr in addresses]
        addresses_info = self.get_addresses_information(addresses, ton_currency_to_show)

        multisigs_info = []
        for address_info in addresses_info:
            try:
                multisig_info = self._parse_multisig_wallet_data_cell(address_info)
            except FailedToParseDataCell:
                multisig_info = None
            multisigs_info.append(multisig_info)

        return addresses_info, multisigs_info

    def _parse_multisig_wallet_data_cell(self, addr_info: AddressInfoResult) -> MultiSigInfo:
        if addr_info.data_cell is None:
            raise FailedToParseDataCell("Data cell not present")
        try:
            return MultiSigInfo.from_data_cell(addr_info.data_cell)
        except Exception as exc:
            raise FailedToParseDataCell(f"Failed to parse data cell: {exc}")

    def get_multisig_order_information(self, addr: Union[Address, str],
                                       ton_currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton,
                                       raise_actions_parse_fail: bool = False) \
            -> Tuple[AddressInfoResult, MultiSigOrderData]:
        tons_logger().debug(f'get multisig order info {addr}')
        addr_info = self.get_address_information(Address(addr).to_string(), ton_currency_to_show)
        order_info = self._parse_multisig_order_data_cell(addr_info, raise_actions_parse_fail)
        return addr_info, order_info

    def get_multisig_orders_information(self, addresses: Sequence[Union[Address, str]],
                                        ton_currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) \
            -> Tuple[List[AddressInfoResult], List[Optional[MultiSigOrderData]]]:
        tons_logger().debug(f'get multisig orders info {len(addresses)}')
        addresses = [Address(addr).to_string() for addr in addresses]
        addresses_info = self.get_addresses_information(addresses, ton_currency_to_show)
        orders_info = []
        for address_info in addresses_info:
            try:
                order_info = self._parse_multisig_order_data_cell(address_info)
            except FailedToParseDataCell:
                order_info = None
            orders_info.append(order_info)
        return addresses_info, orders_info

    def _parse_multisig_order_data_cell(self, addr_info: AddressInfoResult, raise_actions_parse_fail: bool = False) -> MultiSigOrderData:
        if addr_info.data_cell is None:
            raise FailedToParseDataCell('Data cell not present')
        try:
            return MultiSigOrderData.from_data_cell(addr_info.data_cell, raise_actions_parse_fail)
        except Exception as exc:
            raise FailedToParseDataCell(f"Failed to parse data cell: {exc}")

    def _paginate(self, query: DAppGqlIdOrderedQuery):
        previous_last_id = None
        while True:
            query.add_pagination(previous_last_id)
            query_result = self._run_gql_query(query)
            yield from query_result
            try:
                previous_last_id = query_result[-1]['id']
            except IndexError:
                break

    def seqno(self, addr: str) -> int:
        return self.get_address_information(addr).seqno

    def deploy_wallet(self, wallet: WalletContract, wait_for_result: bool = False) -> [Dict, BroadcastResult]:
        tons_logger().info(f'deploy wallet ({type(wallet).__name__})')
        timeout = self.BROADCAST_TIMEOUT if wait_for_result else 0
        query = wallet.create_init_external_message()
        base64_boc = bytes_to_b64str(query["message"].to_boc(False))
        result = self._run(lambda: self.provider.broadcast(
            [BroadcastQuery(boc=base64_boc, timeout=timeout)], timeout=self.REQUEST_TIMEOUT))

        broadcast_result = self._parse_broadcast_result(result, wait_for_result)
        broadcast_result = self._specify_deploy_broadcast_result(broadcast_result,
                                                                 query['message'],
                                                                 wait_for_result)
        return query, broadcast_result

    def _external_message_was_not_accepted(self, exc: TonError):
        return 'external message was not accepted' in f'{exc.detail}'.lower()

    def _specify_deploy_broadcast_result(self, broadcast_result: BroadcastResult,
                                               external_message: Cell,
                                               waited: bool) -> BroadcastResult:
        if not waited:
            return broadcast_result

        tx_info = self._find_transaction(external_message, broadcast_result)
        broadcast_result = self._specify_tx_hash(tx_info, broadcast_result)
        if tx_info.orig_status_name != 'Uninit' or tx_info.end_status_name != 'Active':
            broadcast_result.status = BroadcastStatusEnum.failed
            return broadcast_result

        broadcast_result.status = BroadcastStatusEnum.committed
        return broadcast_result

    def deploy_multisig(self, from_wallet: WalletContract,
                        contract: MultiSigWalletContractV2, wait_for_result=False) -> [Dict, BroadcastResult]:
        tons_logger().info(f'deploy multisig ({type(contract).__name__})')
        deploy_message = self._multisig_deploy_message(contract)
        return self.transfer(from_wallet, [deploy_message], wait_for_result=wait_for_result)

    def _multisig_deploy_message(
            self, contract: MultiSigWalletContractV2) -> InternalMessage:
        state_init = contract.create_init_external_message()['state_init']
        return InternalMessage(
            to_addr=contract.address,
            amount=self.config.multisig.multisig_deploy_amount,
            currency=TonCurrencyEnum.ton,
            state_init=state_init
        )

    def deploy_multisig_order(self, from_wallet: WalletContract,
                              actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]],
                              expiration_date: int, is_signer: bool, address_idx: int, order_id: int, multisig_address: Union[Address, str],
                              wait_for_result: bool = False) -> [Dict, BroadcastResult]:
        order_message = self._get_multisig_order_message(actions, expiration_date, is_signer, address_idx, order_id, multisig_address)
        return self.transfer(from_wallet, [order_message], wait_for_result=wait_for_result)

    def approve_multisig_order(self, from_wallet: WalletContract, signer_idx: int, order_address: Union[str, Address],
                               wait_for_result: bool = False):
        message = pack_multisig_order_approve(signer_idx)
        approve_internal_message = InternalMessage(
            to_addr=Address(order_address),
            amount=self.config.multisig.order_approve_send_amount,
            currency=TonCurrencyEnum.ton,
            body=message
        )
        return self.transfer(from_wallet, [approve_internal_message], wait_for_result=wait_for_result)

    def _get_multisig_order_message(self, actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]],
                       expiration_date: int, is_signer: bool, address_idx: int, order_id: int, multisig_address: Union[Address, str]) -> InternalMessage:
        order_body = new_multisig_order_body(actions, expiration_date, is_signer, address_idx, order_id=order_id)
        order_message = InternalMessage(
            to_addr=Address(multisig_address),
            amount=self.config.multisig.order_deploy_amount,
            currency=TonCurrencyEnum.ton,
            body=order_body
        )
        return order_message

    def transfer(self, from_wallet: WalletContract, messages: List[InternalMessage], wait_for_result=False,
                 attempts=2) -> [Dict, BroadcastResult]:
        """
        Transfer ton from the specified `from_wallet` to the provided list of recipients using internal messages.

        Args:
            from_wallet (WalletContract): The wallet contract from which the funds will be transferred.
            messages (List[InternalMessage]): A list of `InternalMessage` objects representing the transfer details.
            wait_for_result (bool, optional): Determines whether to wait for the transfer result.
                Defaults to False.
            attempts (int, optional): Retry attempts times in case the transfer fails with `exitcode=33`.
                Before retrying, sleep for TRY_AGAIN_SLEEP_SEC seconds, to let the backend update the seqno.
                Defaults to True.

        Returns:
            [Dict, BroadcastResult]: A tuple containing the transfer query and the broadcast result.

        Raises:
            InsufficientBalanceError: If the `from_wallet` does not have sufficient balance to cover the total amount
            of the transfer.

        Note:
            The `wait_for_result` parameter affects the timeout duration for waiting for the transfer result.
            The timeout is set to self.TIMEOUT seconds if `wait_for_result` is True, or 0 seconds if `wait_for_result` is False.
        """
        modes = {message.send_mode for message in messages}
        tons_logger().info(f'transfer (n={len(messages)}, modes={modes})')

        timeout = self.BROADCAST_TIMEOUT if wait_for_result else 0

        addresses = [message.to_addr.to_string() for message in messages] + [from_wallet.address.to_string()]
        addresses_info = self.get_addresses_information(addresses, currency_to_show=TonCurrencyEnum.nanoton)
        from_address_info: AddressInfoResult = addresses_info.pop()

        total_amount = sum([to_nano(message.amount, src_unit=message.currency) for message in messages])
        if total_amount > from_address_info.balance:
            raise InsufficientBalanceError

        for idx, message in enumerate(messages):
            if addresses_info[idx].state in (AddressState.uninit, AddressState.non_exist):
                message.to_addr.is_bounceable = False

        query = from_wallet.create_transfer_message(seqno=from_address_info.seqno, messages=messages,
                                                    timeout=self.TRANSACTION_TIMEOUT, timestamp=self.get_time())
        msg_boc = query["message"].to_boc(False)
        base64_boc = bytes_to_b64str(msg_boc)
        tons_logger().info(f'transfer (seqno={from_address_info.seqno})')

        try:
            result = self._run(lambda: self.provider.broadcast([BroadcastQuery(boc=base64_boc, timeout=timeout)],
                                                               timeout=self.REQUEST_TIMEOUT))
        except TonDappError as dapp_error:
            # TODO:
            #  Fix this, the exitcode should not be parsed from verbose details.
            #  Best solution would be to implement returning exitcode as part of the response from the backend.
            if attempts > 0 and "exitcode=33" in dapp_error.detail:
                sleep(DAppTonClient.TRY_AGAIN_SLEEP_SEC)
                return self.transfer(from_wallet, messages, wait_for_result, attempts=attempts - 1)

            tons_logger().info(f'transfer dapp error ({type(dapp_error).__name__}, '
                               f'seqno={from_address_info.seqno})')
            raise dapp_error

        broadcast_result = self._parse_broadcast_result(result, wait_for_result)
        broadcast_result = self._specify_transfer_broadcast_result(broadcast_result,
                                                                   query['message'],
                                                                   messages,
                                                                   query['valid_until'],
                                                                   wait_for_result)

        tons_logger().info(f'transfer result ({broadcast_result.status}, timeout={int(broadcast_result.timeout)}, '
                           f'seqno={from_address_info.seqno})')

        return query, broadcast_result

    def _specify_transfer_broadcast_result(self, broadcast_result: BroadcastResult,
                                           external_message: Cell,
                                           messages: Sequence[InternalMessage],
                                           valid_until: int,
                                           waited: bool) -> BroadcastResult:
        if not waited:
            return broadcast_result

        try:
            tx_info: TransactionInfo = self._find_transaction(external_message, broadcast_result, valid_until)
        except (TransactionNotCommitted, TransactionNotFound):
            raise
        broadcast_result = self._specify_tx_hash(tx_info, broadcast_result)

        if (tx_info.out_messages is None) or len(tx_info.out_messages) == 0:
            # Possible edge case: balance too low
            broadcast_result.status = BroadcastStatusEnum.failed
            return broadcast_result

        if len(tx_info.out_messages) != len(messages):
            raise TonDappError(f"Messages count mismatch: {len(messages)} requested, "
                               f"{len(tx_info.out_messages)} actually sent")

        addresses_res = {Address.raw_id(msg.dst) for msg in tx_info.out_messages}
        addresses_mine = {Address.raw_id(msg.to_addr) for msg in messages}

        if addresses_res != addresses_mine:
            raise TonDappError(f"Wrong transaction: addresses mismatch")

        broadcast_result.status = BroadcastStatusEnum.committed
        return broadcast_result

    def refresh_dns_ownership(self, from_wallet: WalletContract,
                              dns_items: Sequence[NftItemInfoResult],
                              wait_for_result: bool = False) -> [Dict, BroadcastResult]:
        tons_logger().info(f'refresh dns')
        self._assert_dns_address_consistency(from_wallet, dns_items)

        messages = [self._dns_refresh_internal_message(dns_item) for dns_item in dns_items]

        return self.transfer(from_wallet, messages=messages, wait_for_result=wait_for_result)

    @classmethod
    def _assert_dns_address_consistency(cls, from_wallet: WalletContract, dns_items: Sequence[NftItemInfoResult]):
        for dns_item in dns_items:
            if dns_item.owner_or_max_bidder:
                assert Address(dns_item.owner_or_max_bidder) == from_wallet.address, f"DNS addresses are inconsistent: {dns_item.owner_or_max_bidder} != {from_wallet.address}"

    def _dns_refresh_internal_message(self, dns_item: NftItemInfoResult) -> InternalMessage:
        if dns_item.owner_address:
            amount = self.config.dns.refresh_send_amount
            payload = ""
        else:
            amount = self.config.dns.refresh_not_yet_owned_send_amount
            payload = Cell()
            op_change_dns_record = 0x4eb1f0f9
            query_id = 0
            mock_dict_key = 0
            payload.bits.write_uint(op_change_dns_record, 32)
            payload.bits.write_uint(query_id, 64)
            payload.bits.write_uint(mock_dict_key, 256)

        return InternalMessage(
            to_addr=Address(dns_item.account.address),
            amount=amount,
            currency=TonCurrencyEnum.ton,
            body=payload,
        )

    def jetton_transfer(self, from_wallet: WalletContract, from_jetton_wallet_addr: Address,
                        to_address: Union[str, Address], jetton_amount: int, gas_amount: decimal.Decimal,
                        wait_for_result: bool = False) -> [Dict, BroadcastResult]:
        jetton_transfer_body = JettonWallet().create_transfer_body(to_address=to_address,
                                                                   jetton_amount=jetton_amount,
                                                                   forward_amount=0,
                                                                   forward_payload=None,
                                                                   response_address=from_wallet.address,
                                                                   query_id=0)

        messages = [InternalMessage(
            send_mode=SendModeEnum.ignore_errors,
            to_addr=from_jetton_wallet_addr,
            amount=gas_amount,
            currency=TonCurrencyEnum.ton,
            body=jetton_transfer_body,
        )]

        return self.transfer(from_wallet=from_wallet, messages=messages, wait_for_result=wait_for_result)

    def send_boc(self, boc: bytes, wait_for_result: bool) -> BroadcastResult:
        timeout = self.BROADCAST_TIMEOUT if wait_for_result else 0
        base64_boc = bytes_to_b64str(boc)
        result = self._run(lambda: self.provider.broadcast(
            [BroadcastQuery(boc=base64_boc, timeout=timeout)],
            self.REQUEST_TIMEOUT
        ))

        return self._parse_broadcast_result(result, wait_for_result)

    def _run(self, to_run: Callable, *, single_query=True):
        try:
            results = to_run()
        except DAppWrongResult as e:
            if len(e.errors) == 1 and e.errors[0].code in TON_EXCEPTION_BY_CODE:
                raise TON_EXCEPTION_BY_CODE[e.errors[0].code]

            raise TonDappError(str(e))

        except Exception as e:  # ClientConnectorError, ...?
            exception_text = str(e)
            if not exception_text:
                exception_text = repr(e)

            raise TonDappError(exception_text)

        if single_query:
            return results[0]

        return results

    def _run_gql_query(self, query: Union[DAppGqlQuery, Info, Price]):  # TODO refactor Union
        return self._run(lambda: self.provider.query([query.gql()]))[query.name]

    def _parse_addr_info(self, result: dict, currency_to_show: TonCurrencyEnum = TonCurrencyEnum.ton) \
            -> AddressInfoResult:
        return AddressInfoResult(
            address=result['address'],
            contract_type=result['contract_type'],
            seqno=self._get_seqno(result),
            state=result['acc_type_name'],
            balance=self._get_balance(result, currency_to_show),
            last_activity=self._get_last_paid(result),
            code=result['code'],
            data=result['data'],
        )

    @staticmethod
    def _get_seqno(result: dict) -> int:
        if result['acc_type_name'] in [AddressState.active, AddressState.frozen]:
            # TODO: check contract type and version
            data_cell = Cell.one_from_boc(b64str_to_bytes(result["data"]))
            if len(data_cell.bits) > 32:
                seqno = 0
                for bit in data_cell.bits[:32]:
                    seqno = (seqno << 1) | bit
                return seqno

        return 0

    @staticmethod
    def _get_balance(result: dict, currency_to_show: TonCurrencyEnum) -> decimal.Decimal:
        if "balance" in result and result["balance"]:
            if int(result["balance"]) < 0:
                balance = 0
            else:
                balance = from_nano(int(result["balance"]), currency_to_show)
        else:
            balance = 0

        return decimal.Decimal(balance)

    @staticmethod
    def _get_last_paid(result: dict) -> str:
        if "last_paid" in result and result["last_paid"]:
            return str(datetime.utcfromtimestamp(
                result['last_paid']).strftime('%Y-%m-%d %H:%M:%S'))

    def _parse_broadcast_result(self, result: Dict, waited: bool) -> BroadcastResult:
        if "status" in result:
            if result["status"] == 1 and waited:
                status = BroadcastStatusEnum.committed
            else:
                status = BroadcastStatusEnum.broadcasted
        else:
            status = BroadcastStatusEnum.failed

        return BroadcastResult(timeout=self.BROADCAST_TIMEOUT, status=status, data=result)

    def _find_transaction(self, external_message: Cell, broadcast_result: BroadcastResult,
                          valid_until: Optional[int] = None) -> TransactionInfo:
        in_msg_hash = external_message.bytes_hash().hex()

        try:
            tx_hash = broadcast_result.transaction_hash()
            res = self.get_transaction_information(tx_hash)
            if res is not None:
                return res
        except (TransactionHashNotFound, TonError):
            pass

        tons_logger().info(f"Failed to find tx by hash. Searching by in_msg={in_msg_hash}")
        return self._find_transaction_by_in_msg_hash(in_msg_hash, valid_until)

    @classmethod
    def _specify_tx_hash(cls, tx_info: TransactionInfo, broadcast_result: BroadcastResult) -> BroadcastResult:
        try:
            broadcast_result.transaction_hash()
        except TransactionHashNotFound:
            broadcast_result.set_transaction_hash(tx_info.id)
        return broadcast_result

    def _find_transaction_by_in_msg_hash(self, in_msg_hash: str, valid_until: Optional[int], sleep_time: int = 15,
                                         blockchain_time_fuzz: int = 5) -> TransactionInfo:
        # Possible edge case: timeout for backend request set too low, still may be committed to blockchain
        retries = math.ceil(self.TRANSACTION_TIMEOUT / sleep_time) + 1
        retry_idx = 0
        while retry_idx < retries or self._transfer_should_be_yet_valid(valid_until):
            retry_idx += 1
            try:
                tx_info = self.get_transaction_information_by_in_msg(in_msg_hash)
                if tx_info is not None:
                    tons_logger().info(f"found transaction by in msg")
                    return tx_info
                block = self.get_last_masterchain_block_info(raise_none=True)
            except TonError:
                pass
            else:
                if valid_until is not None:
                    if block.gen_utime > valid_until + blockchain_time_fuzz:
                        raise TransactionNotCommitted
            tons_logger().info(f"(find transaction by in msg) retry {retry_idx}/{retries}")
            sleep(sleep_time)

        raise TransactionNotFound

    def _transfer_should_be_yet_valid(self, valid_until: int, fuzz: int = 120):
        return self.get_time() <= valid_until + fuzz


