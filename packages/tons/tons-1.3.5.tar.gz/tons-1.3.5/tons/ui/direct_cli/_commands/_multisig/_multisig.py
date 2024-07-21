import functools
from typing import Sequence, Optional, Union

import click

from tons.tonclient._client._base import AddressState, AddressInfoResult, FailedToParseDataCell
from tons.tonclient.utils._exceptions import MultiSigRecordDoesNotExistError, MultiSigRecordAlreadyExistsError
from tons.tonclient.utils._multisig import LocalMultiSigRecordList, MultiSigOrderRecord
from tons.tonsdk.contract.wallet import MultiSigConfig, MultiSigWalletContractV2
from tons.tonclient import ton_exceptions_handler
from tons.tonclient.utils import Record, WhitelistContactDoesNotExistError, MultiSigWalletRecord
from tons.tonsdk.utils import Address
from ._utils import validate_save_as, validate_record
from .._base_cmd import cli
from ..._utils import click_ton_exception_handler, with_whitelist, with_keystore, CustomClickException, \
    y_n_to_bool
from ...._utils import SharedObject, display_multisig_info, get_wallet_from_record_ctx, form_multisig_wallet_table, \
    find_extra_info_about_address


@cli.group()
def multisig():
    """
    Operate with multi-owner wallets
    """


@multisig.command(name='list')
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--verbose', '-v', 'verbose', is_flag=True, default=False,
              help="Load info from TON blockchain")
@click.pass_obj
def list_(shared_object: SharedObject, verbose: bool):
    """
    Show multisig wallet list
    """
    records = shared_object.keystore.multisig_wallet_list.get_records()
    addresses = [record.address for record in records]

    if verbose:
        address_infos, multisig_infos = shared_object.ton_client.get_multisigs_information(addresses)
    else:
        address_infos = multisig_infos = [None] * len(records)

    t = form_multisig_wallet_table(records, multisig_infos, address_infos, verbose)
    click.echo(t)


@multisig.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--name', required=False, metavar="MULTISIG_NAME", help='Multisig name', default=None)
@click.option('--address', required=False, metavar="ADDR", help='Multisig address', default=None)
@click.pass_obj
def get(shared_object: SharedObject,
        name: Optional[str],
        address: Optional[str]):
    """
    Get multisig information
    """
    address = get_multisig_address_from_name_or_address(shared_object, name, address)
    address_info, multisig_info = shared_object.ton_client.get_multisig_information(address)
    get_extra_info = functools.partial(find_extra_info_about_address, shared_object)
    display_multisig_info(address_info, multisig_info, get_extra_info)


@multisig.command(name='import')
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--name', required=True, metavar="MULTISIG_NAME", help='Multisig name')
@click.option('--address', required=True, metavar="ADDR", help='Multisig address')
@click.option('-y', '--is_sure', is_flag=True, default=False, help='Do not ask for confirmation if failed to parse data cell')
@click.option('--validate', is_flag=True, default=False, help='Do not import if failed to parse data cell')
@click.pass_obj
def import_(shared_object: SharedObject,
            name: str, address: str, is_sure: bool, validate: bool):
    """
    Import existing multisig
    """
    try:
        shared_object.ton_client.get_multisig_information(address)
    except FailedToParseDataCell:
        if validate:
            raise CustomClickException("Failed to parse data cell. This seems to be an invalid multisig.")
        if not is_sure:
            click.echo('')
            click.confirm(f'Failed to parse data cell. This seems to be an invalid multisig. Add anyway?',
                          abort=True)

    _save_multisig(shared_object, address, name)


def get_multisig_address_from_name_or_address(shared_object: SharedObject, name: Optional[str],
                                              address: Optional[str]) -> Address:
    return get_multisig_entity_address_from_name_or_address(shared_object.keystore.multisig_wallet_list,
                                                            name, address, 'Multisig')


def get_order_address_from_name_or_address(shared_object: SharedObject, name: Optional[str],
                                           address: Optional[str]) -> Address:
    return get_multisig_entity_address_from_name_or_address(shared_object.keystore.multisig_order_list,
                                                            name, address, 'Order')


def get_multisig_entity_address_from_name_or_address(entity_list: LocalMultiSigRecordList,
                                                     name: Optional[str], address: Optional[str], entity_name: str) -> Address:
    if bool(name) == bool(address):
        raise CustomClickException('Either name or address should be specified')

    if name:
        try:
            record = entity_list.get_record(name=name)
        except MultiSigRecordDoesNotExistError:
            raise CustomClickException(f"{entity_name} under the name '{name}' does not exist.")
        address = record.address

    return Address(address)


def pretty_address(address: Union[str, Address]) -> str:
    return Address(address).to_string(is_user_friendly=True, is_bounceable=False, is_url_safe=True)


@multisig.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.option('--deployer', '-d', required=True, metavar='RECORD_NAME', help='Keystore wallet to deploy the contract from')
@click.option('--signer', '-s', metavar='ADDRESS', help='Signer address [multiple]', multiple=True, required=True)
@click.option('--proposer', '-p', metavar="ADDRESS", help='Proposer address [multiple]', multiple=True, required=False, default=None)
@click.option('--threshold', type=int, help='Number of signers required to approve orders (default is equal to number of signers)', default=None)
@click.option('--allow-arbitrary-seqno', type=click.Choice(['y', 'n']), default='y', callback=y_n_to_bool,
              show_default=True, help='Allow arbitrary seqno (advanced)' )
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.option('--save_as', metavar='MULTISIG_NAME', help='Save the deployed multisig as', default=None)
@click.option('--initial_order_seqno', metavar='UINT256', help='Initial order seqno (advanced)', default=0, show_default=True)
@click.pass_obj
def deploy(shared_object: SharedObject,
           deployer: str,
           signer: Sequence[str],
           proposer: Optional[Sequence[str]],
           threshold: Optional[int],
           allow_arbitrary_seqno: bool,
           wait: bool,
           save_as: Optional[str],
           initial_order_seqno: int):
    """
    Deploy the multisig contract
    """
    deployer_record = validate_record(shared_object, deployer)
    save_as = validate_save_as(shared_object, save_as)

    if threshold is None:
        threshold = len(signer)

    try:
        multisig_contract = MultiSigWalletContractV2(
            config=MultiSigConfig(
                threshold=threshold,
                signers=signer,
                proposers=proposer,
                allow_arbitrary_seqno=allow_arbitrary_seqno,
                initial_seqno=initial_order_seqno
            )
        )
    except Exception as exc:
        raise CustomClickException(repr(exc))

    multisig_address = _get_multisig_address(multisig_contract)

    multisig_address_info = _get_multisig_address_info(shared_object, multisig_contract)
    if multisig_address_info.state != AddressState.uninit:
        """ Should raise, since the multisig contract supports update of contract data and it is not guaranteed to be the same."""
        msg = f'Address is already initialized: {multisig_address}. Try a different initial_seqno'
        raise CustomClickException(msg)
    else:
        _deploy_multisig(shared_object, deployer_record, multisig_contract, wait)
        if wait:
            multisig_address_info = _get_multisig_address_info(shared_object, multisig_contract)
            if multisig_address_info.state == AddressState.active:
                click.echo(f'Contract deployed to {multisig_address}')
            else:
                click.echo(f'Failed to verify deployment to {multisig_address}. Please check manually.')
        else:
            click.echo(f'Deployment transaction to {multisig_address}')

    if save_as:
        _save_multisig(shared_object, address=multisig_address, name=save_as)


def _save_multisig(shared_object: SharedObject, address: Union[Address, str], name: str):
    record = MultiSigWalletRecord(
        address=address,
        name=name
    )
    l = shared_object.keystore.multisig_wallet_list
    try:
        with l.restore_on_failure():
            l.add_record(record)
            l.save()
    except MultiSigRecordAlreadyExistsError as exc:
        raise CustomClickException(str(exc))

    click.echo(f'Multisig wallet is saved under the name {name}.')


def _get_multisig_address_info(shared_object: SharedObject, multisig_contract: MultiSigWalletContractV2) -> AddressInfoResult:
    return shared_object.ton_client.get_address_information(_get_multisig_address(multisig_contract))


def _get_multisig_address(multisig_contract: MultiSigWalletContractV2) -> str:
    return pretty_address(multisig_contract.address)


def _deploy_multisig(shared_object: SharedObject, deployer_record: Record, multisig_contract: MultiSigWalletContractV2,
                     wait: bool):
    from_wallet = get_wallet_from_record_ctx(shared_object, deployer_record)
    _, res = shared_object.ton_client.deploy_multisig(from_wallet,
                                                      multisig_contract,
                                                      wait)
    click.echo(res)
