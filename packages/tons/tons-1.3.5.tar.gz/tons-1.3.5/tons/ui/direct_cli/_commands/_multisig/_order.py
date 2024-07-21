from typing import List

from tons.tonclient.utils import WhitelistContact, RecordDoesNotExistError
from tons.tonsdk.contract.wallet import MultiSigOrderData
from tons.ui._utils import display_order_info, form_multisig_order_table
from ._multisig import *


@multisig.group()
def order():
    """
    Operate with orders
    """


@order.command(name='list')
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--verbose', '-v', 'verbose', is_flag=True, default=False,
              help="Load info from TON blockchain")
@click.pass_obj
def list_(shared_object: SharedObject, verbose: bool):
    """
    Show multisig order list
    """
    records = shared_object.keystore.multisig_order_list.get_records()
    addresses = [record.address for record in records]

    if verbose:
        address_infos, order_infos = shared_object.ton_client.get_multisig_orders_information(addresses)
    else:
        address_infos = order_infos = [None] * len(records)

    t = form_multisig_order_table(records, order_infos, address_infos, verbose)
    click.echo(t)


@order.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=False)
@click.option('--name', required=False, metavar="NAME", help='Order name', default=None)
@click.option('--address', required=False, metavar="ADDR", help='Order address', default=None)
@click.pass_obj
def get(shared_object: SharedObject, name: Optional[str], address: Optional[str]):
    """
    Get order information
    """
    address = get_order_address_from_name_or_address(shared_object, name, address)
    address_info, order_info = shared_object.ton_client.get_multisig_order_information(address)
    get_extra_info = functools.partial(find_extra_info_about_address, shared_object)
    display_order_info(address_info, order_info, get_extra_info)


def _get_order_address_from_name(shared_object: SharedObject, order_name: str) -> Address:
    return get_order_address_from_name_or_address(shared_object, order_name, None)


@order.command(name='import')
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--name', required=True, metavar="ORDER_NAME", help='Order name')
@click.option('--address', required=True, metavar="ADDR", help='Order address')
@click.option('-y', '--is_sure', is_flag=True, default=False, help='Do not ask for confirmation if failed to parse data cell')
@click.option('--validate', is_flag=True, default=False, help='Do not import if failed to parse data cell')
@click.pass_obj
def import_(shared_object: SharedObject,
            name: str, address: str, is_sure: bool, validate: bool):
    """
    Import existing multisig
    """
    try:
        shared_object.ton_client.get_multisig_order_information(address)
    except FailedToParseDataCell:
        if validate:
            raise CustomClickException("Failed to parse data cell. This seems to be an invalid order.")
        if not is_sure:
            click.echo('')
            click.confirm(f'Failed to parse data cell. This seems to be an invalid order. Add anyway?',
                          abort=True)

    _save_order(shared_object, address, name)


def _save_order(shared_object: SharedObject, address: Union[Address, str], name: str):
    record = MultiSigOrderRecord(
        address=address,
        name=name
    )
    l = shared_object.keystore.multisig_order_list
    try:
        with l.restore_on_failure():
            l.add_record(record)
            l.save()
    except MultiSigRecordAlreadyExistsError as exc:
        raise CustomClickException(str(exc))

    click.echo(f'Multisig order is saved under the name {name}.')


@order.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.option('--order', 'order_', required=True, metavar="NAME", help='Order name', type=str)
@click.option('--signer', '-s', metavar='NAME', help='Signer wallet to sign the order [multiple]', multiple=True, required=True)
@click.option('-y', '--is_sure', is_flag=True, default=False, help='Do not ask for confirmation')
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.pass_obj
def approve(shared_object: SharedObject, order_: str, signer: Sequence[str], is_sure: bool, wait: bool):
    order_address = _get_order_address_from_name(shared_object, order_)

    address_info, order_info = shared_object.ton_client.get_multisig_order_information(order_address)
    _validate_order_can_be_approved(order_info)

    signer_records = _validate_signers(shared_object, signer)
    _validate_signers_are_present_in_multisig_contract(order_info, signer_records)

    if not is_sure:
        display_order_info(address_info, order_info)
        click.echo('')
        click.confirm(f'Please carefully review the details of this order. Are you sure you want to approve it?', abort=True)

    for signer_record in signer_records:
        click.echo(f'{signer_record.name}:  sending approval...')
        signer_idx = order_info.signers.index(Address(signer_record.address))
        if order_info.approved_by(signer_idx):
            click.echo(f'Order is already approved by this wallet ({signer_record.address_to_show})')
            continue

        from_wallet = get_wallet_from_record_ctx(shared_object, signer_record)

        _, res = shared_object.ton_client.approve_multisig_order(from_wallet, signer_idx, order_address, wait)
        click.echo(f'{signer_record.name}:  {res}')


def _validate_order_can_be_approved(order_info: MultiSigOrderData):
    if order_info.expired():
        raise CustomClickException('The order has expired.')
    if order_info.executed:
        raise CustomClickException('This order has already been executed.')


def _validate_signers_are_present_in_multisig_contract(order_info: MultiSigOrderData, signer_records: Sequence[Record]):
    for signer_record in signer_records:
        _validate_signer_is_present_in_multisig_contract(order_info, signer_record.address, signer_record.name)


def _validate_signer_is_present_in_multisig_contract(order_info: MultiSigOrderData,
                                                     signer_address: Union[str, Address],
                                                     signer_name: str):
    if Address(signer_address) not in order_info.signers:
        raise CustomClickException(f"{signer_name} is not a signer.")


def _validate_signers(shared_object: SharedObject, signer_names: Sequence[str]) -> List[Record]:
    try:
        return [
            shared_object.keystore.get_record_by_name(signer_name, raise_none=True)
            for signer_name in signer_names
        ]
    except RecordDoesNotExistError as exc:
        raise CustomClickException(repr(exc))

