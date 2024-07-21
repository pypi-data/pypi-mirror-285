from functools import wraps
from typing import Optional

import click

from tons import settings
from tons.tonclient import ton_exceptions_handler
from tons.tonclient.utils import WhitelistContactAlreadyExistsError, WhitelistContactDoesNotExistError, \
    KeyStoreDoesNotExistError, BaseWhitelist
from tons.tonsdk.utils import InvalidAddressError, TonCurrencyEnum, Address
from ._base_cmd import cli
from .._utils import CustomClickException, with_whitelist, click_ton_exception_handler, click_echo_success, \
    initialize_keystore
from ..._utils import SharedObject, form_whitelist_table


@cli.group()
def whitelist():
    """
    Operate with whitelist contacts
    """


def with_keystore_if_local(func):
    @click.pass_obj
    @click.option('--local', '-l', is_flag=True, default=False,
                  help="Use local keystore whitelist")
    @click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
                  help='Required for "yubikey" keystore if --local specified')
    @wraps(func)
    def magic(shared_object: SharedObject, local, pin, *args, **kwargs):
        if local:
            initialize_keystore(shared_object, sensitive=False, pin=pin)
        return func(local, *args, **kwargs)

    return magic


@whitelist.command()
@with_whitelist
@with_keystore_if_local
@click.argument('name', required=True)
@click.argument('address', required=True)
@click.pass_obj
def add(shared_object: SharedObject, local: bool, name: str, address: str, ):
    """
    Add a contact to the whitelist
    """
    try:
        __get_whitelist(shared_object, local).add_contact(name, address, save=True)
    except (PermissionError, FileNotFoundError, WhitelistContactAlreadyExistsError, InvalidAddressError) as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"contact {name} has been added to the {'local ' if local else ''}whitelist.")


@whitelist.command()
@with_whitelist
@with_keystore_if_local
@click.argument('name', required=True)
@click.pass_obj
def get(shared_object: SharedObject, local: bool, name: str):
    """
    Get a contact address by its name
    """
    try:
        contact = __get_whitelist(shared_object, local).get_contact(name, raise_none=True)
    except WhitelistContactDoesNotExistError as e:
        raise CustomClickException(repr(e))

    addr = Address(contact.address)
    click.echo(f"Raw address: {addr.to_string(False, False, False)}")
    click.echo(f"Nonbounceable address: {addr.to_string(True, True, False)}")
    click.echo(f"Bounceable address: {addr.to_string(True, True, True)}")


@whitelist.command()
@with_whitelist
@with_keystore_if_local
@click.argument('name', required=True, metavar="EXISTING_CONTACT_NAME")
@click.option('--name', '-n', 'new_name', help="Set a new name")
@click.option('--address', '-a', 'new_address', help="Set a new address")
@click.pass_obj
def edit(shared_object: SharedObject, local: bool, name: str, new_name: str, new_address: str):
    """
    Edit contact in a whitelist
    """
    try:
        __get_whitelist(shared_object, local).edit_contact(name, new_name, new_address, save=True)
    except (WhitelistContactDoesNotExistError, ValueError) as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"contact {name} has been edited.")


@whitelist.command()
@with_whitelist
@with_keystore_if_local
@click.argument('name', required=True)
@click.pass_obj
def delete(shared_object: SharedObject, local: bool, name: str, ):
    """
    Delete contact from a whitelist
    """
    try:
        __get_whitelist(shared_object, local).delete_contact_by_name(name, save=True)
    except WhitelistContactDoesNotExistError as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"contact {name} has been deleted.")


@whitelist.command(name='list')
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@click.option('--local', '-l', is_flag=True, default=False, help="Use local keystore whitelist")
@click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
              help='Required for "yubikey" keystore (if --global-only not specified)')
@click.option('--currency', '-c', default=TonCurrencyEnum.ton, show_default=True,
              type=click.Choice(TonCurrencyEnum))
@click.option('--verbose', '-v', 'verbose', is_flag=True, default=False,
              help="Extra information from TON")
@click.option('--global-only', '-g', 'global_only', is_flag=True, default=False,
              help="Show only contacts from the global whitelist")
@click.pass_obj
def list_(shared_object: SharedObject, pin: Optional[str], local: bool, verbose: bool, currency: TonCurrencyEnum,
          global_only: bool):
    """
    Print all contacts as a Markdown table.
    You can output this command into a .md file
    """
    if local and global_only:
        raise CustomClickException("You cannot use --local and --global-only at the same time.")

    if not global_only:
        initialize_keystore(shared_object, sensitive=False, pin=pin)

    def __display_whitelist(_whitelist: BaseWhitelist, title: str):
        contacts = _whitelist.get_contacts(shared_object.config.tons.sort_whitelist)
        contact_infos = shared_object.ton_client.get_addresses_information(
            [contact.address for contact in contacts], currency) if verbose else None
        table = form_whitelist_table(contacts, verbose, contact_infos, title)
        click.echo(table)

    if local or not global_only:
        __display_whitelist(shared_object.keystore.whitelist, f'{shared_object.keystore.name} whitelist')
    if global_only or not local:
        __display_whitelist(shared_object.whitelist, 'Global whitelist')


@whitelist.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@click.argument('contact_name', metavar='CONTACT', required=True)
@click.option('--from-keystore', help="Source keystore whitelist", default=None, metavar='KEYSTORE')
@click.option('--to-keystore', help="Destination keystore whitelist", default=None, metavar='KEYSTORE')
@click.option('--from-global', is_flag=True, default=False,
              help="Move from the global whitelist")
@click.option('--to-global', is_flag=True, default=False,
              help="Move to the global whitelist")
@click.option('--delete', '-d', 'remove_old', is_flag=True, default=False,
              help="Remove contact from the old whitelist")
@click.pass_obj
def move(shared_object: SharedObject, contact_name: str, from_keystore: Optional[str], to_keystore: Optional[str],
         from_global: bool, to_global: bool, remove_old: bool):
    """
    Move contact to local or global whitelist
    """
    if bool(from_keystore) == from_global:
        raise CustomClickException("Specify one of these: --from-keystore KEYSTORE, --from-global")
    if bool(to_keystore) == to_global:
        raise CustomClickException("Specify one of these: --to-keystore KEYSTORE, --to-global")
    if ((from_keystore is not None) and (from_keystore == to_keystore)) or (from_global and to_global):
        raise CustomClickException("The source and destination must be different")

    whitelist_src = __get_whitelist_from_name(shared_object, from_keystore, from_global)
    whitelist_dst = __get_whitelist_from_name(shared_object, to_keystore, to_global)

    try:
        contact = whitelist_src.get_contact(contact_name, raise_none=True)
    except WhitelistContactDoesNotExistError as e:
        raise CustomClickException(repr(e))

    try:
        whitelist_dst.add_contact(contact.name, contact.address, contact.default_message, True)
    except WhitelistContactAlreadyExistsError as e:
        raise CustomClickException(repr(e))

    if remove_old:
        whitelist_src.delete_contact(contact, True)

    click_echo_success(f'contact {contact.name} has been successfully {"moved" if remove_old else "copied"} '
                       f'from {"global" if from_global else from_keystore} whitelist '
                       f'to {"global" if to_global else to_keystore} whitelist')


def __get_whitelist(ctx: SharedObject, local: bool):
    return ctx.keystore.whitelist if local else ctx.whitelist


def __get_whitelist_from_name(ctx: SharedObject, keystore_name: Optional[str], global_: bool) -> BaseWhitelist:
    assert bool(keystore_name) != global_
    if keystore_name:
        try:
            keystore = initialize_keystore(ctx, keystore_name=keystore_name, to_shared_keystore=False)
            return keystore.whitelist
        except KeyStoreDoesNotExistError as e:
            raise CustomClickException(repr(e))
    return ctx.whitelist
