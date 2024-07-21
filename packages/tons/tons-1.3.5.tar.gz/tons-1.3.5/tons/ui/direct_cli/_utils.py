import typing as t
from functools import wraps
from gettext import gettext as _
from json import JSONDecodeError

import click
from click import ClickException
from click._compat import get_text_stderr

from tons import settings
from tons.tonclient import TonError
from tons.tonclient.utils import GlobalWhitelist, KeyStores, \
    KeyStoreDoesNotExistError, InvalidKeyStoreError, KeyStoreIsNotSpecifiedError, BaseKeyStore, \
    WhitelistContactDoesNotExistError, RecordDoesNotExistError, WhitelistContactType
from tons.tonclient.utils._keystores import KeyStoreTypeEnum
from tons.tonsdk.boc import Cell
from tons.tonsdk.contract.wallet import SendModeEnum
from tons.ui._utils import SharedObject

PRETTY_CONTACT_TYPE_NAMES = {'wallet': WhitelistContactType.keystore,
                             'local':  WhitelistContactType.local,
                             'global': WhitelistContactType.global_}


class CustomClickException(ClickException):
    def show(self, file: t.Optional[t.IO] = None) -> None:
        if file is None:
            file = get_text_stderr()

        click.echo(_("{error}: {message}").format(
            error=click.style('Error', fg='red'),
            message=self.format_message()), file=file, err=True)


def click_echo_success(msg):
    click.echo("{success}: {message}".format(
        success=click.style('Success', fg='green'),
        message=msg
    ))


def with_whitelist(func):
    @click.pass_obj
    @wraps(func)
    def wrapper(shared_object: SharedObject, *args, **kwargs):
        try:
            shared_object.whitelist = GlobalWhitelist(shared_object.config.tons.whitelist_path)
        except JSONDecodeError:
            raise CustomClickException(
                f"Invalid json in the whitelist file: {shared_object.config.tons.whitelist_path}")

        return func(*args, **kwargs)

    return wrapper


def with_daemon(func):
    @click.pass_obj
    @wraps(func)
    def wrapper(shared_object: SharedObject, *args, **kwargs):
        shared_object.ton_daemon.start()
        return func(*args, **kwargs)

    return wrapper


def with_keystores(func):
    @click.pass_obj
    @wraps(func)
    def wrapper(shared_object: SharedObject, *args, **kwargs):
        shared_object.keystores = KeyStores(shared_object.config.tons.keystores_path)

        return func(*args, **kwargs)

    return wrapper


def initialize_keystore(shared_object: SharedObject, sensitive: bool = False, pin: t.Optional[str] = None,
                        password: t.Optional[str] = None, keystore_name: t.Optional[str] = None,
                        to_shared_keystore: bool = True) -> BaseKeyStore:
    keystores = KeyStores(shared_object.config.tons.keystores_path)
    if keystore_name is None:
        keystore_name = shared_object.config.tons.keystore_name

    try:
        keystore = keystores.get_keystore(keystore_name, raise_none=True)
        if keystore.has_been_upgraded:
            click.echo(keystore_upgrade_message(keystore))

        if keystore.type == KeyStoreTypeEnum.yubikey:
            if not pin:
                pin = click.prompt("Yubikey PIN[]", hide_input=True)
            KeyStores.unlock_keystore(keystore, pin=pin)
        elif keystore.type == KeyStoreTypeEnum.password and sensitive:
            if not password:
                password = click.prompt("Password[]", hide_input=True)
            KeyStores.enter_sensitive(keystore, password=password)

    except (KeyStoreDoesNotExistError, InvalidKeyStoreError, KeyStoreIsNotSpecifiedError) as e:
        raise CustomClickException(repr(e))

    if to_shared_keystore:
        shared_object.keystore = keystore

    return keystore


def keystore_upgrade_message(keystore: BaseKeyStore) -> str:
    """
    Returns a message indicating that the keystore has been upgraded.

    Args:
        keystore (BaseKeyStore): Keystore object.

    Returns:
        str: Message about the keystore being upgraded.
    """
    return f"⚠ Keystore '{keystore.name}' has been upgraded from version {keystore.upgrade_info.old_version} " \
           f"to version {keystore.version}.\n" \
           f"⚠ Old version has been saved to '{keystore.upgrade_info.backup_path}'"


def with_keystore(sensitive_data: bool):
    def without_sensitive_data(func):
        @click.pass_obj
        @click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
                      help='Required only for a "yubikey" type keystore')
        @wraps(func)
        def without_password_wrapper(shared_object: SharedObject, pin, *args, **kwargs):
            initialize_keystore(shared_object, sensitive=False, pin=pin)
            return func(*args, **kwargs)

        return without_password_wrapper

    def with_sensitive_data(func):
        @click.pass_obj
        @click.option("--password", default=settings.KEYSTORE_PASSWORD, show_default=False,
                      help='Required only for a "password" type keystore')
        @click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
                      help='Required only for a "yubikey" type keystore')
        @wraps(func)
        def with_password_wrapper(shared_object: SharedObject, password, pin, *args, **kwargs):
            initialize_keystore(shared_object, sensitive=True, pin=pin, password=password)
            return func(*args, **kwargs)

        return with_password_wrapper

    return with_sensitive_data if sensitive_data else without_sensitive_data


def with_address(func):
    @with_whitelist
    @with_keystore(sensitive_data=False)
    @click.option('--address', '-a', help='Show info by an address')
    @click.option('--wallet', '-w', help='Show info by a wallet name')
    @click.option('--contact', '-c', help='Show info by a whitelist contact name')
    @click.pass_obj
    @wraps(func)
    def wrapper(shared_object: SharedObject, address, wallet, contact, *args, **kwargs):
        if not any([address, wallet, contact]):
            raise click.MissingParameter(
                param=click.Option(['--address', '--wallet', '--contact']))

        if address:
            pass
        elif wallet:
            try:
                wallet_obj = shared_object.keystore.get_record_by_name(
                    wallet, raise_none=True)
            except RecordDoesNotExistError as e:
                raise CustomClickException(repr(e))

            address = wallet_obj.address
        else:
            try:
                contact_obj = shared_object.whitelist.get_contact(contact) or \
                              shared_object.keystore.whitelist.get_contact(contact)
                if contact_obj is None:
                    raise WhitelistContactDoesNotExistError(f"Contact with the name {contact} does not exist")
            except WhitelistContactDoesNotExistError as e:
                raise CustomClickException(repr(e))

            address = contact_obj.address

        kwargs["address"] = address

        return func(*args, **kwargs)

    return wrapper


def click_ton_exception_handler(exception: TonError):
    raise CustomClickException(exception)


class HiddenPassword(object):
    def __init__(self, password=''):
        self.password = password

    def __str__(self):
        return '*' * len(self.password)


def y_n_to_bool(ctx, param, value):
    return value == "y"


def get_send_mode(pay_gas_separately: bool, ignore_errors: bool, destroy_if_zero: bool,
                   transfer_all: bool) -> int:   # TODO DRY
    send_mode = 0
    if ignore_errors:
        send_mode |= SendModeEnum.ignore_errors
    if pay_gas_separately:
        send_mode |= SendModeEnum.pay_gas_separately
    if destroy_if_zero:
        send_mode |= SendModeEnum.destroy_account_if_zero
    if transfer_all:
        send_mode |= SendModeEnum.carry_all_remaining_balance

    return send_mode


def read_boc_from_file(file_path: str) -> Cell:  # TODO DRY
    try:
        with open(file_path, 'rb') as file_obj:
            body_bytes = file_obj.read()
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
        raise CustomClickException(f"Failed to open file: '{file_path}'")
    try:
        return Cell.one_from_boc(body_bytes)
    except Exception:
        raise CustomClickException(f"Failed to parse bag of cells in {file_path}")