import dataclasses
import os
import sys
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Iterable, Tuple, List, Dict, Sequence, Iterator, Any, Union, Callable
from xmlrpc.client import Boolean

import click
import requests
from colorama import Fore
from dateutil.relativedelta import relativedelta
from prettytable import MARKDOWN, PrettyTable
from pydantic import BaseModel, root_validator

from tons import settings
from tons.config import init_config, Config, TonProviderEnum
from tons.tonclient import TonClient, DAppTonClient
from tons.tonclient._client._base import NftItemInfoResult, TonDaemon, AddressInfoResult
from tons.tonclient._client._dapp._daemon import DAppBroadcastDaemon
from tons.tonclient.utils import KeyStores, GlobalWhitelist, BaseKeyStore, Record, WhitelistContact, \
    WhitelistContactType, RecordDoesNotExistError, WhitelistContactDoesNotExistError, contact_type_description, \
    MultiSigWalletRecord, MultiSigOrderRecord
from tons.tonsdk.utils import from_nano, TonCurrencyEnum, Address
from tons.tonsdk.utils.tonconnect.requests_responses import SendTransactionRequest, AppRequestMethodEnum
from ._exceptions import WhitelistContactAmbiguityError
from tons.utils import storage
from tons.utils.versioning import tons_is_outdated
from ..tonclient.utils._exceptions import MultiSigRecordDoesNotExistError
from ..tonclient.utils._keystores._keystore._secret import WalletSecretKind
from ..tonsdk.boc import MessageRelaxed, CommonMessageInfoRelaxedInternal, Cell, CurrencyCollection
from ..tonsdk.contract.wallet import MultiSigInfo, WalletContract, Wallets, MultiSigTransferRequest, \
    MultiSigUpdateRequest, MultiSigOrderData


@dataclasses.dataclass
class SharedObject:
    config: Config
    ton_client: TonClient
    ton_daemon: TonDaemon
    specific_config_path: Optional[str]
    background_task_manager: Optional["BackgroundTaskManager"] = None  # noqa: F821
    keystores: Optional[KeyStores] = None
    keystore: Optional[BaseKeyStore] = None
    whitelist: Optional[GlobalWhitelist] = None
    debug_mode: Boolean = False
    extra: Optional[Dict] = None


class TxAction(str, Enum):
    confirm = "Confirm"
    cancel = "Cancel"


def get_wallet_contact(ctx: SharedObject, contact_name: str,
                       keystore: Optional[BaseKeyStore] = None, raise_none: bool = False) -> \
        Optional[WhitelistContact]:

    """
    Searches for a wallet named `contact_name` in the keystore and converts it to a `WhitelistContact` object.

    Args:
        ctx (SharedObject):
            The shared object (UI context).
        contact_name (str):
            The name of the contact (wallet) to search for.
        keystore (BaseKeyStore, optional):
            The keystore to search in. If not provided, the keystore from `ctx` will be used.
        raise_none (bool, optional):
            If True, raises a `WhitelistContactDoesNotExistError` if the wallet with the name
            `contact_name` is not found. Defaults to False.

    Returns:
        Optional[WhitelistContact]:
            A `WhitelistContact` object representing the found wallet or None if the wallet is not found.

    Raises:
        WhitelistContactDoesNotExistError:
            If the wallet with the name `contact_name` does not exist in the keystore
            (suppressed if `raise_none` is set to False)
    """

    try:
        record = (keystore or ctx.keystore).get_record_by_name(contact_name, raise_none=True)
    except RecordDoesNotExistError:
        if raise_none:
            raise WhitelistContactDoesNotExistError(f"Record {contact_name} does not exist")
        return
    else:
        return WhitelistContact(name=record.name, address=record.address_to_show)


def get_contact(ctx: SharedObject,
                contact_name: str,
                contact_type: Optional[WhitelistContactType] = None) -> WhitelistContact:
    """
    Get a whitelist contact from three sources:
    - global whitelist
    - local whitelist
    - keystore wallets

    Args:
        ctx (SharedObject):
            The shared object (UI context)
        contact_name (str):
            The name of the contact to search for
        contact_type (WhitelistContactType, optional):
            The whitelist contact source. If specified, the search will be restricted to this contact type.

    Raises:
        `WhitelistContactAmbiguityError`:
            when contact with `contact_name` exists in more than one source and `contact_type` has not been specified

    Returns:
        The found `WhitelistContact` object.
    """

    discovered_contacts = dict()

    # Search for a wallet
    try:
        discovered_contacts[WhitelistContactType.keystore] = \
            get_wallet_contact(ctx, contact_name, raise_none=True)
    except WhitelistContactDoesNotExistError:
        pass

    # Search for a local contact
    try:
        discovered_contacts[WhitelistContactType.local] = \
            ctx.keystore.whitelist.get_contact(contact_name, raise_none=True)
    except WhitelistContactDoesNotExistError:
        pass

    # Search for a global contact
    try:
        discovered_contacts[WhitelistContactType.global_] = \
            ctx.whitelist.get_contact(contact_name, raise_none=True)
    except WhitelistContactDoesNotExistError:
        pass

    if contact_type:
        # Contact type has been specified
        try:
            contact = discovered_contacts[contact_type]
        except KeyError:
            raise WhitelistContactDoesNotExistError(
                f"Contact with the name '{contact_name}' "
                f"has not been found in {contact_type_description(contact_type)}"
            )
        return contact

    # Contact type has not been specified
    if len(discovered_contacts) > 1:
        raise WhitelistContactAmbiguityError(contact_name=contact_name,
                                             contact_types=tuple(discovered_contacts.keys()))

    for contact_type in (WhitelistContactType.keystore,
                         WhitelistContactType.local,
                         WhitelistContactType.global_):
        try:
            return discovered_contacts[contact_type]
        except KeyError:
            pass
    else:
        raise WhitelistContactDoesNotExistError(f"Contact with the name '{contact_name}' does not exist")


def init_shared_object(specific_config_path: str = None) -> SharedObject:
    config = init_config(specific_config_path)
    ton_client = get_ton_client(config)
    ton_daemon = get_ton_daemon(config, ton_client)

    return SharedObject(
        config=config, specific_config_path=specific_config_path, ton_client=ton_client, ton_daemon=ton_daemon)


def setup_app(config: Config):
    if config.tons.warn_if_outdated and tons_is_outdated():
        print("\033[93mWarning: tons version is outdated! "
              "Please, see the update guide: https://tonfactory.github.io/tons-docs/installation#update\033[0m")

    for default_dir_path in [config.tons.workdir,
                             config.tons.keystores_path]:
        try:
            storage.ensure_dir_exists(default_dir_path)
        except PermissionError as e:
            raise PermissionError(f'Workdir "{e.filename}" inaccessible or unmounted.')


def get_ton_client(config: Config):
    if config.tons.provider == TonProviderEnum.dapp:
        return DAppTonClient(config)
    else:
        raise NotImplementedError


def get_ton_daemon(config: Config, client: TonClient) -> TonDaemon:
    if config.tons.provider == TonProviderEnum.dapp:
        assert isinstance(client, DAppTonClient), "Provided client is not of DAppTonClient type"
        return DAppBroadcastDaemon(config, client)
    else:
        raise NotImplementedError


def pin_is_valid(pin: str):
    if len(pin) != 6:
        return False

    return True


class CustomPrettyTable(PrettyTable):
    def get_string(self, **kwargs):
        self.align["Name"] = 'l'
        self.align["Comment"] = 'l'
        self.align["Balance"] = 'r'

        return super().get_string()


def md_table() -> CustomPrettyTable:
    table = CustomPrettyTable()
    table.set_style(MARKDOWN)
    return table


def form_wallets_table(wallets_info: Tuple[Record],
                       verbose: bool,
                       wallets_verbose_info: Optional[List[AddressInfoResult]] = None,
                       total_required: bool = False):
    # wallet list, whitelist list
    field_names = ['Name', 'Version', 'WC', 'Address', 'Comment']
    if verbose:
        field_names += ['State', 'Balance']

    table = md_table()
    table.field_names = field_names
    if verbose:
        total = 0
        for wallet, wallet_info in zip(wallets_info, wallets_verbose_info):
            total += wallet_info.balance
            table.add_row([wallet.name, wallet.version, wallet.workchain,
                           wallet.tep_standard_user_address, wallet.comment,
                           wallet_info.state.value, format(wallet_info.balance, 'f')])
        if wallets_info and total_required:
            table.add_row(["Total", "", "", "", "", "", format(total, 'f')])
    else:
        for wallet in wallets_info:
            table.add_row([wallet.name, wallet.version, wallet.workchain,
                           wallet.tep_standard_user_address, wallet.comment])

    return table


def form_tonconnect_table(connections):
    table = md_table()
    table.field_names = ["Wallet", "Connected at", "Dapp Name", "Dapp Url", "Dapp Client Id"]
    for connection in connections:
        table.add_row([connection.wallet_name, connection.connected_datetime,
                       connection.app_manifest.name, connection.app_manifest.url, connection.dapp_client_id])

    return table


def form_whitelist_table(contacts: Tuple[WhitelistContact],
                         verbose: bool,
                         contact_infos: Optional[List[AddressInfoResult]] = None,
                         title: Optional[str] = None):
    field_names = ["Contact name", "Address", "Message"]
    if verbose:
        field_names += ['State', 'Balance']

    table = md_table()
    if title:
        table.title = title
    table.field_names = field_names
    table.align["Contact name"] = 'l'
    table.align["Message"] = 'l'
    if verbose:
        for contact, contact_info in zip(contacts, contact_infos):
            table.add_row([contact.name, contact.address_to_show, contact.default_message,
                           contact_info.state.value, format(contact_info.balance, 'f')])

    else:
        for contact in contacts:
            table.add_row([contact.name, contact.address_to_show, contact.default_message])

    return table


def form_dns_table(dns_items_info: Iterable[NftItemInfoResult], display_not_owned=True) -> CustomPrettyTable:
    """
    Form a DNS table based on the provided DNS item information.

    Args:
        dns_items_info (Iterable[NftItemInfoResult]): Iterable containing DNS item information.
        display_not_owned (bool, optional): Determines whether to display items that are not owned
        but have won auctions. Defaults to True.

    Returns:
        CustomPrettyTable: A formatted table containing DNS domain information.

    Note:
        The table includes the following fields:
        - "DNS domain": The domain name for the DNS item.
        - "Last fill-up time": The timestamp of the last fill-up time (GMT).
        - "Expires in": The remaining time in days until the item's expiration.

        If `display_not_owned` is True, the table will also include the following field:
        - "Status": The status of the DNS item, indicating whether it is owned or won in an auction.

        The field "Owner" will be renamed to "Owner / max bidder" if `display_not_owned` is True.
    """
    field_names = ["DNS domain", "Last fill-up time", "Expires in"]
    if display_not_owned:
        field_names.append("Owner / max bidder")
        field_names.append("Status")
    else:
        field_names.append("Owner")
    table = md_table()
    table.field_names = field_names

    for dns_item in dns_items_info:
        if not display_not_owned and not dns_item.owner_address:
            continue
        dns_domain = dns_item.dns_domain + '.ton'
        last_fill_up_time = str(datetime.utcfromtimestamp(dns_item.dns_last_fill_up_time)) + ' GMT'
        expires_in = f"{(datetime.utcfromtimestamp(dns_item.dns_expires) - datetime.now()).days} days"  # TODO fix datetime.now() - timezone
        status = 'owned' if dns_item.owner_address else 'auction won'
        row = [dns_domain, last_fill_up_time, expires_in, dns_item.owner_or_max_bidder]
        if display_not_owned:
            row.append(status)

        table.add_row(row)

    return table


def form_multisig_wallet_table(multisig_wallet_records: Sequence[MultiSigWalletRecord],
                               multisig_wallet_info: Sequence[Optional[MultiSigInfo]],
                               multisig_address_info: Sequence[Optional[AddressInfoResult]],
                               verbose: bool = True) -> CustomPrettyTable:
    table = md_table()
    table.field_names = _get_multisig_wallet_table_names(verbose)

    for record, info, addr_info in zip(multisig_wallet_records, multisig_wallet_info, multisig_address_info):
        row = _get_multisig_wallet_table_row(addr_info, info, record, verbose)
        table.add_row(row)
    return table


def _get_multisig_wallet_table_row(addr_info: Optional[AddressInfoResult], info: Optional[MultiSigInfo],
                                   record: MultiSigWalletRecord, verbose: bool) -> List[str]:
    row = [record.name,
           record.address_to_show(),
           record.comment, ]
    if verbose:
        row += [
            '--' if info is None else info.threshold,
            '--' if info is None else len(info.signers),
            '--' if info is None else len(info.proposers),

            '--' if addr_info is None else addr_info.balance,
            '--' if addr_info is None else (addr_info.last_activity or '')]
    return row


def _get_multisig_wallet_table_names(verbose: bool) -> List[str]:
    field_names = ['Name', 'Address', 'Comment' ]
    if verbose:
        field_names += ['Threshold', 'Signers', 'Proposers', 'Balance', 'Last activity']
    return field_names


def _transfer_desc(action: MultiSigTransferRequest) -> str:
    if isinstance(action.message, Cell):
        return f'{Fore.RED}⚠ unknown transfer{Fore.RESET}'
    if isinstance(action.message, MessageRelaxed):
        value: CurrencyCollection = action.message.info.value
        if value.other is None:
            amt = from_nano(value.coins, TonCurrencyEnum.ton)
            amt = format(amt, "f").rstrip('0')
            return f'send {amt}'
        return f'{Fore.RED}⚠ unknown transfer value{Fore.RESET}'
    raise ValueError(f'Unknown transfer message type: {type(action.message)}')


def _action_desc(action: Union[MultiSigTransferRequest, MultiSigUpdateRequest, None]) -> str:
    if isinstance(action, MultiSigUpdateRequest):
        return 'update multisig params'
    if isinstance(action, MultiSigTransferRequest):
        return _transfer_desc(action)
    if action is None:
        return f'{Fore.RED}⚠ unknown action{Fore.RESET}'
    raise ValueError(f'Unknown action type: {type(action)}')


def _actions_desc(order: MultiSigOrderData) -> str:
    if order.actions is None:
        return f'{Fore.RED}⚠ failed to parse{Fore.RESET}'

    to_join = []
    for action in order.actions:
        to_join.append(_action_desc(action))

    return ', '.join(to_join)


def form_multisig_order_table(multisig_order_records: Sequence[MultiSigOrderRecord],
                              multisig_orders_info: Sequence[Optional[MultiSigOrderData]],
                              multisig_addresses_info: Sequence[AddressInfoResult],
                              verbose: bool = True) -> CustomPrettyTable:
    table = md_table()
    table.field_names = _get_multisig_order_table_field_names(verbose)

    for record, info, addr_info in zip(multisig_order_records, multisig_orders_info, multisig_addresses_info):
        row = _get_multisig_order_table_row(addr_info, info, record, verbose)
        table.add_row(row)
    return table


def _get_multisig_order_table_field_names(verbose: bool) -> List[str]:
    if verbose:
        return ['Name', 'Address', 'Comment', 'Status', 'Approvals', 'Actions', 'Balance']

    return ['Name', 'Address', 'Comment',]


def _get_multisig_order_table_row(addr_info: Optional[AddressInfoResult],
                                  info: Optional[MultiSigOrderData],
                                  record: MultiSigOrderRecord,
                                  verbose: bool) -> List[str]:
    def status(order: MultiSigOrderData) -> str:
        if order.executed:
            return 'Executed'
        if order.expired():
            return 'Expired'
        return 'Awaiting approvals'

    def approvals(order: MultiSigOrderData) -> str:
        return f'{order.approvals_num}/{order.threshold}'

    row = [
        record.name,
        record.address_to_show(),
        record.comment]
    if verbose:
        row += [
            '--' if info is None else status(info),
            '--' if info is None else approvals(info),
            '--' if info is None else _actions_desc(info)
            ]
        row += [
            '--' if addr_info is None else format(addr_info.balance, 'f'),
        ]
    return row


def form_request_info(req: SendTransactionRequest):
    if req.method == AppRequestMethodEnum.send_transaction:
        params_info = []
        for i, param in enumerate(req.params):
            messages_str = "\n".join(
                [
                    f"* Send {from_nano(int(message.amount), TonCurrencyEnum.ton)} TON "
                    f"to {Address(message.address).to_string(True)}"
                    for message in
                    param.messages])

            valid_until = ""
            if param.valid_until is not None:
                valid_until = f"valid until {datetime.fromtimestamp(int(param.valid_until) / 10 ** 3)}, "
            params_info.append(f"Operation {i + 1} ({valid_until}"
                               f"request to send {len(param.messages)} messages)\n{messages_str}")

        return "\n".join(params_info)

    else:
        raise NotImplementedError(f"Request with the method '{req.method}' is not implemented.")


def dns_expires_soon(dns_item: NftItemInfoResult, months_max_expiring_in: int) -> bool:
    return datetime.utcfromtimestamp(dns_item.dns_expires) < dns_expire_soon_threshold(months_max_expiring_in)


def dns_expire_soon_threshold(months_max_expiring_in: int) -> datetime:
    if months_max_expiring_in == 12:
        return datetime.utcnow() + relativedelta(days=366)
    return datetime.utcnow() + relativedelta(months=months_max_expiring_in)


def shorten_dns_domain(domain):
    if len(domain) > 25:
        domain = domain[:11] + '...' + domain[-11:]
    return domain


def split_into_lines(text: str, line_max_length: int = 48):
    return '\n'.join(text[i:i + line_max_length] for i in range(0, len(text), line_max_length))


def truncate(text: str, max_len: int = 100):
    if len(text) > max_len:
        return text[:max_len - 3] + '...'
    return text


def fetch_known_jettons():
    """
    Fetches a list of known jettons from https://github.com/tonkeeper/ton-assets
    :raises: requests.RequestException, requests.JSONDecodeError
    :return: parsed json of known jetton addresses
    """
    response = requests.get(settings.KNOWN_JETTONS_URL)
    response.raise_for_status()
    return response.json()


def fetch_known_jettons_addresses() -> Tuple[Address, ...]:
    """
    Fetches a list of known jettons from https://github.com/tonkeeper/ton-assets
    Returns:
        Tuple[Address]: A tuple containing the list of known jetton addresses.
        If the fetch fails, an empty tuple is returned.
    """
    try:
        return tuple(Address(jetton['address']) for jetton in fetch_known_jettons())
    except (requests.RequestException, requests.JSONDecodeError):
        return tuple()


def getcwd_pretty():
    return os.getcwd().replace(os.sep, "/")


def batches(seq: Sequence, batch_size: int) -> Iterator[Sequence[Any]]:
    for i in range(0, len(seq), batch_size):
        yield seq[i:i+batch_size]


def _pretty_address(address: Union[str, Address]) -> str:
    return Address(address).to_string(is_user_friendly=True, is_bounceable=False, is_url_safe=True)


def display_multisig_address_info(address_info: AddressInfoResult):
    click.echo(f"Address:  {_pretty_address(address_info.address)}")
    click.echo(f"Balance:  {format(address_info.balance, 'f')}")  # ton


def display_multisig_info(address_info: AddressInfoResult, multisig_info: MultiSigInfo,
                          get_extra_address_info: Optional[Callable[[Union[Address, str]], str]] = None):
    get_extra_address_info = get_extra_address_info or (lambda _: '')
    display_multisig_address_info(address_info)

    click.echo(f"Signers:")
    for signer in multisig_info.signers:
        echo_list_item_address(signer, get_extra_address_info(signer))
    if multisig_info.proposers:
        click.echo(f"Proposers:")
        for proposer in multisig_info.proposers:
            echo_list_item_address(proposer, get_extra_address_info(proposer))

    click.echo(f"Threshold:  {multisig_info.threshold}")

    click.echo(f"Allow arbitrary order seqno:  {multisig_info.allow_arbitrary_seqno}")

    next_order_seqno = multisig_info.next_order_seqno
    if next_order_seqno is None:
        next_order_seqno = '--'
    click.echo(f"Next order seqno:  {next_order_seqno}")


def echo_list_item_address(addr: Union[str, Address], extra: str = '', prefix: str = ''):
    click.echo(f"{prefix}- {_pretty_address(addr)}  {extra}")


def get_wallet_from_record_ctx(shared_object: SharedObject, record: Record) -> WalletContract:
    keystore = shared_object.keystore
    contract, _ = keystore.get_wallet_from_record(record)
    return contract


def _display_action(action: Union[MultiSigTransferRequest, MultiSigUpdateRequest],
                    multisig_address: Union[Address, str],
                    get_extra_address_info: Optional[Callable[[Union[Address, str]], str]] = None):
    get_extra_address_info = get_extra_address_info or (lambda _: '')

    if action is None:
        click.echo('- Failed to parse', err=True)
    elif isinstance(action, MultiSigTransferRequest):
        _display_transfer_request(action, multisig_address, get_extra_address_info)
    elif isinstance(action, MultiSigUpdateRequest):
        _display_update_request(action, get_extra_address_info)
    else:
        raise NotImplementedError


def _display_transfer_request(action: MultiSigTransferRequest,
                              multisig_address: Union[Address, str],
                              get_extra_address_info: Callable[[Union[Address, str]], str]):

    bad = ((not isinstance(action.message, MessageRelaxed)) or
           (not isinstance(action.message.info, CommonMessageInfoRelaxedInternal)) or
           (action.message.info.value.other is not None))

    if bad:
        click.echo('- Transfer')
        click.echo('  FAILED TO PARSE MESSAGE CELL:')
        assert isinstance(action.message, Cell)
        click.echo(f"{action.message.to_string(indent='  ')}")
        return

    assert isinstance(action.message.info, CommonMessageInfoRelaxedInternal)
    amount = from_nano(action.message.info.value.coins, dst_unit=TonCurrencyEnum.ton)

    click.echo(f'- Transfer')
    click.echo(f'  amount:  {format(amount, "f")} TON')
    if action.message.info.src is not None:
        if Address(multisig_address) != Address(action.message.info.src):
            click.echo(f'  from:  {_pretty_address(action.message.info.src)}  '
                       f'{get_extra_address_info(action.message.info.src)}')
    click.echo(f'  to:  {_pretty_address(action.message.info.dest)}    {get_extra_address_info(action.message.info.dest)}')

    if not action.message.body.empty():
        click.echo(f'  body:')
        click.echo(f'{action.message.body.to_string(indent="    ")}')

    if action.message.init is not None:
        click.echo(f'  init:')
        click.echo(f'{action.message.init.to_string(indent="    ")}')


def _display_update_request(action: MultiSigUpdateRequest,
                            get_extra_address_info: Callable[[Union[Address, str]], str]):
    click.echo(f'- Update multisig parameters:')
    click.echo(f'  new threshold: {action.threshold}')
    click.echo(f'  new signers:')
    for signer in action.signers:
        echo_list_item_address(signer, prefix='  ', extra=get_extra_address_info(signer))
    click.echo(f'  new proposers:')
    for proposer in action.proposers:
        echo_list_item_address(proposer, prefix='  ', extra=get_extra_address_info(proposer))


def _get_order_pretty_status(order_info: MultiSigOrderData) -> str:
    if order_info.executed:
        return 'Executed'
    if order_info.expired():
        return 'Expired'
    return 'Awaiting approvals'


def display_order_info(address_info: AddressInfoResult, order_info: MultiSigOrderData,
                       get_extra_address_info: Optional[Callable[[Union[Address, str]], str]] = None,
                       use_red: bool = True):

    get_extra_address_info = get_extra_address_info or (lambda _ : '')
    display_multisig_address_info(address_info)

    click.echo(f"Multisig address:  {_pretty_address(order_info.multisig_address)}  "
               f"{get_extra_address_info(order_info.multisig_address)}")
    click.echo(f"Order ID (seqno):  {order_info.order_seqno}")
    click.echo(f"Approvals:  {order_info.approvals_num} / {order_info.threshold}")

    status = _get_order_pretty_status(order_info)
    click.echo(f"Status:  {status}")

    click.echo(f"Expires:  {order_info.expiration_utc_datetime()} UTC")

    click.echo(f"Signers ({len(order_info.signers)}):")

    space = '            ' if order_info.approvals_num > 0 else ''

    for idx, signer in enumerate(order_info.signers):
        extra = '(approved ✓)' if order_info.approved_by(idx) else space
        extra += '  ' + get_extra_address_info(signer)
        echo_list_item_address(signer, extra)

    if order_info.failed_to_parse_actions():
        click.echo("Actions:")
        msg = "⚠ FAILED TO PARSE ACTIONS. It is not recommended to sign this order."
        if use_red:
            msg = f"{Fore.RED}{msg}{Fore.RESET}"

        click.echo(msg)
        return

    click.echo(f"Actions ({len(order_info.actions)}):")
    for action in order_info.actions:
        _display_action(action, order_info.multisig_address, get_extra_address_info)


def find_extra_info_about_address(ctx: SharedObject, addr: Union[Address, str]) -> str:
    """ Gets extra info about address (whether it is a record, whitelist contact, etc) """
    # wallets
    record = ctx.keystore.get_record_by_address(addr)
    if record is not None:
        return WhitelistContact.pretty_string(record.name, WhitelistContactType.keystore)

    # multisigs
    try:
        record = ctx.keystore.multisig_wallet_list.get_record(address=addr)
    except MultiSigRecordDoesNotExistError:
        pass
    else:
        return record.pretty_string()

    # local whitelist
    contact = ctx.keystore.whitelist.get_contact_by_address(Address(addr).to_string())
    if contact is not None:
        return WhitelistContact.pretty_string(contact.name, WhitelistContactType.local)

    # global whitelist
    contact = ctx.whitelist.get_contact_by_address(Address(addr).to_string())
    if contact is not None:
        return WhitelistContact.pretty_string(contact.name, WhitelistContactType.global_)

    return ''


class RecipientKind(Enum):
    record = auto()
    local_contact = auto()
    global_contact = auto()


class Recipient(BaseModel):
    entity: Union[Record, WhitelistContact]
    kind: RecipientKind

    @root_validator(pre=False)
    def _validate_consistency(cls, values):
        try:
            if values['kind'] == RecipientKind.record:
                assert isinstance(values['entity'], Record)
            elif values['kind'] in [RecipientKind.local_contact, RecipientKind.global_contact]:
                assert isinstance(values['entity'], WhitelistContact)
            else:
                assert False
        except AssertionError:
            raise ValueError(f'kind/entity type inconsistency: {values["kind"]} vs {values["entity"]}')
        return values


def get_recipient_by_address(keystore: BaseKeyStore, global_whitelist: GlobalWhitelist,
                             address: Union[Address, str]) -> Optional[Recipient]:
    try:
        return Recipient(
            entity=keystore.get_record_by_address(address, True),
            kind=RecipientKind.record
        )
    except RecordDoesNotExistError:
        pass

    try:
        return Recipient(
            entity=keystore.whitelist.get_contact_by_address(address, True),
            kind=RecipientKind.local_contact
        )
    except WhitelistContactDoesNotExistError:
        pass

    try:
        return Recipient(
            entity=global_whitelist.get_contact_by_address(address, True),
            kind=RecipientKind.global_contact
        )
    except WhitelistContactDoesNotExistError:
        pass
