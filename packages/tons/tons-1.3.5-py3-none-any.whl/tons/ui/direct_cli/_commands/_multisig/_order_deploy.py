from decimal import Decimal
from typing import Tuple
import datetime

from tons.tonsdk.contract.wallet import get_multisig_order_address, MultiSigInfo, MultiSigUpdateRequest, \
    MultiSigTransferRequest
from tons.tonsdk.utils import TonCurrencyEnum
from tons.ui._exceptions import WhitelistContactAmbiguityError
from tons.ui._utils import get_contact
from ._order import *
from ._order import _save_order
from ._utils import validate_save_as, validate_record
from ..._utils import PRETTY_CONTACT_TYPE_NAMES, y_n_to_bool, get_send_mode, read_boc_from_file


@order.group()
def deploy():
    """
    Deploy order
    """


@deploy.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.option('--amount', required=False, metavar='TON_COINS_NUM', help='Amount of the coins to send', default=None)
@click.option('--multisig', 'multisig_', required=True, metavar='NAME', help='Multisig name')
@click.option('--deployer', required=True, metavar='WALLET', help='Deployer wallet from the keystore. Must be either signer or proposer')
@click.option('--destination', '--dst', required=True, metavar='CONTACT_NAME', help='Contact to send transaction to')
@click.option('--contact_type', 'contact_type', default=None, show_default=True,
              type=click.Choice(PRETTY_CONTACT_TYPE_NAMES.keys()),
              help='Restrict the destination contact search to a specific whitelist')
@click.option('--expiry', required=False, metavar='TIMESTAMP', help='UTC timestamp of expiration date (default = 30 days from now)', default=None, type=int)
@click.option('--order_id', required=False, metavar='SEQNO', help='Manually specify order ID (advanced)', default=None, type=int)
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.option('--pay-gas-separately', default="y", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--ignore-errors', default="n", type=click.Choice(["y", "n"]), show_default=True,
              help='Bounce back if error occurs', callback=y_n_to_bool)
@click.option('--destroy-if-zero', default="n", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--transfer-all', default="n", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--save_as', metavar='NAME', help='Save the contract as', default=None)
@click.option('--body', metavar='FILE', required=False, help="Path to a file containing the body (bag of cells)")
@click.option('--state-init', metavar='FILE', required=False,
              help='Path to a file containing the state init (bag of cells)')
@click.pass_obj
def transfer(shared_object: SharedObject, multisig_: str, deployer: str, expiry: Optional[int], destination: str,
             contact_type: str, wait: bool, pay_gas_separately: bool, ignore_errors: bool, destroy_if_zero: bool,
             transfer_all: bool, body: str, state_init: str, amount, order_id: Optional[int], save_as: Optional[str]):
    """
    Deploy a transfer order
    """

    expiry, save_as, deployer_record, multisig_record = _validate_order_deploy_common_info(shared_object,
                                                                                           expiry, save_as,
                                                                                           deployer, multisig_)

    addr_info, multisig_info = shared_object.ton_client.get_multisig_information(multisig_record.address)
    is_signer, address_idx = _deployer_is_signer(deployer_record, multisig_info)  # TODO multisig_info method

    contact = _validate_destination(shared_object, destination, contact_type)
    send_mode = get_send_mode(pay_gas_separately, ignore_errors, destroy_if_zero, transfer_all)
    transfer_all, amount = _validate_amount_and_transfer_all(transfer_all, amount)

    if body is not None:
        body = read_boc_from_file(body)

    if state_init is not None:
        state_init = read_boc_from_file(state_init)

    actions = [
        MultiSigTransferRequest.send_ton(
            amount = Decimal(amount),
            currency = TonCurrencyEnum.ton,
            src = multisig_record.address,
            dest = contact.address,
            body = body,
            init = state_init,
            send_mode = send_mode
        )
    ]

    order_id = _validate_order_id(order_id, multisig_info)

    deployer_wallet = get_wallet_from_record_ctx(shared_object, deployer_record)

    order_address = get_multisig_order_address(Address(multisig_record.address), order_seqno=order_id)
    _echo_brief_order_info(order_address, order_id)
    _check_order_address(shared_object, order_address)
    _, res = shared_object.ton_client.deploy_multisig_order(deployer_wallet, actions, expiry, is_signer, address_idx,
                                                            order_id, multisig_record.address, wait)

    click.echo(res)

    if save_as:
        _save_order(shared_object, order_address, save_as)


@deploy.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.option('--multisig', 'multisig_', required=True, metavar='CONTACT',
              help='Multisig as recorded in local whitelist')
@click.option('--deployer', required=True, metavar='WALLET',
              help='Deployer wallet from the keystore. Must be either signer or proposer')
@click.option('--signer', '-s', metavar='ADDRESS', help='Signer address [multiple]', multiple=True, required=True)
@click.option('--proposer', '-p', metavar="ADDRESS", help='Proposer address [multiple]', multiple=True, required=False,
              default=None)
@click.option('--threshold', type=int,
              help='Number of signers required to approve orders (default is equal to number of signers)', default=None)
@click.option('--allow-arbitrary-seqno', 'allow_arbitrary_seqno', type=click.Choice(['y', 'n']), default='y',
              callback=y_n_to_bool,
              show_default=True, help='Allow arbitrary seqno (advanced)')
@click.option('--expiry', required=False, metavar='TIMESTAMP',
              help='UTC timestamp of expiration date (default = 30 days from now)', default=None, type=int)
@click.option('--order_id', required=False, metavar='SEQNO', help='Manually specify order ID (advanced)', default=None,
              type=int)
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.option('--save_as', metavar='NAME', help='Save the contract as', default=None)
@click.pass_obj
def update(shared_object: SharedObject, multisig_: str, deployer: str, expiry: Optional[int], signer: Sequence[str],
           proposer: Optional[Sequence[str]], threshold: Optional[int], allow_arbitrary_seqno: bool,
           order_id: Optional[int], wait: bool, save_as: Optional[str]):
    """
    Deploy an order to update the multisig params
    """
    expiry, save_as, deployer_record, multisig_record = _validate_order_deploy_common_info(shared_object,
                                                                                           expiry, save_as,
                                                                                           deployer, multisig_)

    addr_info, multisig_info = shared_object.ton_client.get_multisig_information(multisig_record.address)

    is_signer, address_idx = _deployer_is_signer(deployer_record, multisig_info)  # TODO multisig_info method

    if threshold is None:
        threshold = len(signer)

    try:
        actions = [
            MultiSigUpdateRequest(
                threshold = threshold,
                proposers = proposer,
                signers = signer
            )
        ]
    except Exception as exc:
        raise CustomClickException(repr(exc))

    order_id = _validate_order_id(order_id, multisig_info)

    deployer_wallet = get_wallet_from_record_ctx(shared_object, deployer_record)

    order_address = get_multisig_order_address(Address(multisig_record.address), order_seqno=order_id)
    _echo_brief_order_info(order_address, order_id)
    _check_order_address(shared_object, order_address)

    _, res = shared_object.ton_client.deploy_multisig_order(deployer_wallet, actions, expiry, is_signer, address_idx,
                                                            order_id, multisig_record.address, wait)

    click.echo(res)

    if save_as:
        _save_order(shared_object, order_address, save_as)


def _validate_order_deploy_common_info(shared_object: SharedObject,
                                       expiry: Optional[int],
                                       save_as: Optional[str],
                                       deployer: str,
                                       multisig_: str) -> Tuple[int, Optional[str], Record, MultiSigWalletRecord]:
    expiry = _validate_expiry(expiry)
    save_as = validate_save_as(shared_object, save_as)
    deployer_record = validate_record(shared_object, deployer)
    multisig_record = _validate_multisig(shared_object, multisig_)

    return expiry, save_as, deployer_record, multisig_record


def _echo_brief_order_info(order_address: Union[str, Address], order_id: int):
    click.echo(f"Order address:  {pretty_address(order_address)}")
    click.echo(f"Order ID:  {order_id}")


def _check_order_address(shared_object: SharedObject, order_address: Union[Address, str]):
    order_address_info = shared_object.ton_client.get_address_information(order_address.to_string())
    if order_address_info.state != AddressState.uninit:
        raise CustomClickException('Order address is taken. Try a different order_id')


def _validate_expiry(expiry: Optional[int]) -> int:
    if expiry is None:
        expiry = datetime.datetime.now().timestamp() + 30 * 24 * 3600
    else:
        now = datetime.datetime.utcnow()
        expires = datetime.datetime.utcfromtimestamp(expiry)
        if now > expires:
            raise CustomClickException('Expiry is in the past')

    return int(expiry)


def _validate_order_id(order_id: Optional[int], multisig_info: 'MultiSigInfo') -> int:
    if order_id is None:
        order_id = multisig_info.get_next_order_seqno()
    try:
        multisig_info.validate_order_seqno(order_id)
    except ValueError as exc:
        raise CustomClickException(repr(exc))
    return order_id


def _validate_multisig(shared_object: SharedObject, name: str) -> MultiSigWalletRecord:
    try:
        return shared_object.keystore.multisig_wallet_list.get_record(name=name)
    except MultiSigRecordDoesNotExistError as exc:
        raise CustomClickException(str(exc))


def _validate_amount_and_transfer_all(transfer_all: bool,
                                      amount: Optional[Union[Decimal, str, int, float]]) -> Tuple[bool, Decimal]:
    if bool(transfer_all) == (amount is not None):
        raise CustomClickException('Either specify the amount or transfer_all')
    if transfer_all:
        amount = 0
    return transfer_all, Decimal(amount)


def _deployer_is_signer(deployer_record: Record, multisig_info: 'MultiSigInfo') -> Tuple[bool, int]:
    is_signer, address_idx = multisig_info.get_is_signer_and_address_idx(deployer_record.address)
    if address_idx is None:
        raise CustomClickException(f"{deployer_record.name} is not a proposer or a signer.")

    return is_signer, address_idx


def _validate_destination(shared_object: SharedObject, destination: str, contact_type: Optional[str]) -> WhitelistContact:
    try:
        contact = get_contact(shared_object, destination, PRETTY_CONTACT_TYPE_NAMES.get(contact_type, None))
    except (WhitelistContactDoesNotExistError, WhitelistContactAmbiguityError) as exc:
        raise CustomClickException(repr(exc))

    return contact


def _shorten_order_id(order_id: int) -> str:
    order_id = str(order_id)
    if len(order_id) <= 10:
        return order_id
    order_id = order_id[:4] + '..' + order_id[-4:]
    return order_id

