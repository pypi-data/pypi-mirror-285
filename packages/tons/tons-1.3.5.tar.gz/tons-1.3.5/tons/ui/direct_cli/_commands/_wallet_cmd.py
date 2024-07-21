import os
from typing import Optional

import click

from tons.tonclient import ton_exceptions_handler
from tons.tonclient._client._base import AddressState
from tons.tonclient.utils import RecordAlreadyExistsError, RecordDoesNotExistError, \
    WhitelistContactDoesNotExistError, KeyStoreInvalidPasswordError, InvalidMnemonicsError, KeyStoreDoesNotExistError
from tons.tonsdk.boc import Cell
from tons.tonsdk.contract.wallet import SendModeEnum, WalletVersionEnum, Wallets, WalletContract, InternalMessage
from tons.tonsdk.crypto._payload_encryption import encrypt_message
from tons.tonsdk.utils import TonCurrencyEnum, Address
from tons.utils import storage
from ._base_cmd import cli
from .._utils import CustomClickException, with_whitelist, with_keystore, click_ton_exception_handler, \
    click_echo_success, y_n_to_bool, with_keystores, keystore_upgrade_message, PRETTY_CONTACT_TYPE_NAMES
from ..._exceptions import WhitelistContactAmbiguityError
from ..._utils import SharedObject, form_wallets_table, get_contact


def __parse_subwallet_id_after_workchain(ctx: SharedObject, version: Optional[WalletVersionEnum], workchain: int,
                                         subwallet_id: int):
    if version is None:
        version = ctx.config.tons.default_wallet_version
    return WalletContract.default_subwallet_id(workchain, version) \
        if subwallet_id is None else subwallet_id


@cli.group()
def wallet():
    """
    Operate with wallets
    """


@wallet.command()
@with_keystore(sensitive_data=False)
@with_whitelist
@click.argument('name', required=True)
@click.option('--version', '-v', type=click.Choice(WalletVersionEnum))
@click.option('--workchain', '-wc', default=0, show_default=True, type=int)
@click.option('--subwallet-id', '-id', type=int,
              help="Extra field for v3 and v4 versions. "
                   "Leave empty to use default 698983191 + workchain")
@click.option('--comment', help='Extra information about the wallet')
@click.option('--save-to-whitelist', 'contact_name', help='Contact name to save to global whitelist', metavar='NAME')
@click.pass_obj
def create(shared_object: SharedObject, name: str, version: WalletVersionEnum, workchain: int, subwallet_id: int,
           comment: str, contact_name: str):
    """
    Create wallet data and add it to the keystore
    """
    subwallet_id = __parse_subwallet_id_after_workchain(shared_object, version, workchain,
                                                        subwallet_id)

    if contact_name:
        contact = shared_object.whitelist.get_contact(contact_name)
        if contact is not None:
            raise CustomClickException(
                f"Contact with the name '{contact_name}' already exists")

    if version is None:
        version = WalletVersionEnum(
            shared_object.config.tons.default_wallet_version)

    try:
        mnemonics, _, _, wallet_ = Wallets.create(version, workchain, subwallet_id)
        shared_object.keystore.add_new_record(name, mnemonics, version,
                                              workchain, subwallet_id, comment, save=True)
    except RecordAlreadyExistsError as e:
        raise CustomClickException(repr(e))

    if contact_name:
        shared_object.whitelist.add_contact(
            contact_name, wallet_.address.to_string(True), save=True)

    click_echo_success(f"wallet {name} has been created.")


@wallet.command()
@with_keystore(sensitive_data=False)
@with_whitelist
@click.argument('name', required=True)
@click.option('--name', '-n', 'new_name', help='New wallet name')
@click.option('--comment', '-c', 'new_comment', help='New extra information about the wallet')
@click.pass_obj
def edit(shared_object: SharedObject, name: str, new_name: str, new_comment: str):
    """
    Edit wallet data in a keystore
    """
    try:
        shared_object.keystore.edit_record(
            name, new_name, new_comment, save=True)
    except (RecordDoesNotExistError, RecordAlreadyExistsError) as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"wallet {name} has been edited.")


@wallet.command()
@with_keystore(sensitive_data=False)
@with_whitelist
@click.argument('name', required=True)
@click.option('--yes', '-y', 'is_sure', is_flag=True, help='Do not show the prompt')
@click.pass_obj
def delete(shared_object: SharedObject, name: str, is_sure: bool):
    """
    Delete wallet data from a keystore
    """
    if not is_sure:
        click.confirm(
            f'Are you sure you want to delete {name} wallet?', abort=True)

    try:
        shared_object.keystore.delete_record(name, save=True)
    except RecordDoesNotExistError as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"wallet {name} has been deleted.")


@wallet.command()
@with_keystore(sensitive_data=False)
@with_whitelist
@click.argument('name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Load info about wallet from TON network')
@click.pass_obj
def get(shared_object: SharedObject, name: str, verbose: bool):
    """
    Get all wallet data from a keystore
    """
    try:
        wallet_record = shared_object.keystore.get_record_by_name(
            name, raise_none=True)
    except RecordDoesNotExistError as e:
        raise CustomClickException(repr(e))

    addr = Address(wallet_record.address)
    if verbose:
        addr_info = shared_object.ton_client.get_address_information(
            wallet_record.address)

    click.echo(f"Raw address: {addr.to_string(False, False, False)}")
    click.echo(f"Nonbounceable address: {addr.to_string(True, True, False)}")
    click.echo(f"Bounceable address: {addr.to_string(True, True, True)}")
    click.echo(f"Version: {wallet_record.version}")
    click.echo(f"Workchain: {wallet_record.workchain}")
    click.echo(f"Subwallet id: {wallet_record.subwallet_id}")
    click.echo(f"Comment: {wallet_record.comment}")

    if verbose:
        click.echo("--- Verbose wallet information ---")
        for k, v in addr_info.dict().items():
            click.echo(str(k) + ': ' + str(v))


@wallet.command(name='list')
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystore(sensitive_data=False)
@click.option('--currency', '-c', default=TonCurrencyEnum.ton, show_default=True,
              type=click.Choice(TonCurrencyEnum))
@click.option('--verbose', '-v', 'verbose', is_flag=True, default=False,
              help="Extra information from TON")
@click.pass_obj
def list_(shared_object: SharedObject, verbose: bool, currency: TonCurrencyEnum):
    """
    Print all wallets info as a markdown table.
    You can output this command into .md file
    """
    wallets = shared_object.keystore.get_records(shared_object.config.tons.sort_keystore)
    wallet_infos = None
    if verbose:
        wallet_infos = shared_object.ton_client.get_addresses_information(
            [wallet.address for wallet in wallets], currency)

    table = form_wallets_table(wallets, verbose, wallet_infos, True)

    click.echo(table)


@wallet.command()
@with_keystore(sensitive_data=False)
@with_whitelist
@click.argument('name', required=True)
@click.argument('version', type=click.Choice(WalletVersionEnum))
@click.argument('workchain', type=int)
@click.argument('mnemonics')
@click.option('--subwallet-id', '-id', type=int,
              help="Extra field for v3 and v4 versions. "
                   "Leave empty to use default 698983191 + workchain")
@click.option('--comment', help='Extra information about the wallet')
@click.option('--save-to-whitelist', 'contact_name', help='Contact name to save', metavar='NAME')
@click.pass_obj
def import_from_mnemonics(shared_object: SharedObject, name: str, version: WalletVersionEnum,
                          workchain: int, mnemonics: str, subwallet_id: int, comment: str,
                          contact_name: str):
    """
    Create wallet data from mnemonics and add it to the keystore
    """
    subwallet_id = __parse_subwallet_id_after_workchain(shared_object, version, workchain,
                                                        subwallet_id)
    if contact_name:
        contact = shared_object.whitelist.get_contact(contact_name)
        if contact is not None:
            raise CustomClickException(
                f"Contact with the name '{contact_name}' already exists")

    mnemonics = mnemonics.split(" ")
    try:
        shared_object.keystore.add_new_record(name, mnemonics, version,
                                              workchain, subwallet_id, comment, save=True)
    except (RecordAlreadyExistsError, InvalidMnemonicsError) as e:
        raise CustomClickException(repr(e))

    if contact_name:
        shared_object.whitelist.add_contact(
            contact_name, wallet.address.to_string(True), save=True)

    click_echo_success(f"wallet {name} has been imported.")


@wallet.command()
@with_keystore(sensitive_data=True)
@click.argument('name', required=True)
@click.pass_obj
def reveal(shared_object: SharedObject, name: str):
    """
    Echo mnemonics of a wallet by its name
    """
    try:
        record = shared_object.keystore.get_record_by_name(
            name, raise_none=True)
        secret = shared_object.keystore.get_secret(record)

        if secret.mnemonics:
            click.echo(secret.mnemonics)
        else:
            raise CustomClickException("Mnemonics are not present in this record. Likely imported from a private key.")

    except (RecordDoesNotExistError, KeyStoreInvalidPasswordError) as e:
        raise CustomClickException(repr(e))


@wallet.command()
@with_keystore(sensitive_data=True)
@click.argument('name', required=True)
@click.argument('destination_dir', default=".", required=False, metavar='DESTINATION_DIR')
@click.pass_obj
def to_addr_pk(shared_object: SharedObject, name: str, destination_dir: str):
    """
    Export wallet to .pk and .addr file into a specified directory
    """
    try:
        record = shared_object.keystore.get_record_by_name(
            name, raise_none=True)

        secret = shared_object.keystore.get_secret(record)
        pk = secret.private_key[:32]
        addr = Address(record.address).to_buffer()

        addr_path = os.path.join(
            destination_dir, record.name + ".addr")
        pk_path = os.path.join(destination_dir, record.name + ".pk")
        storage.save_bytes(addr_path, addr)
        storage.save_bytes(pk_path, pk)

    except (RecordDoesNotExistError, KeyStoreInvalidPasswordError, OSError) as e:
        raise CustomClickException(repr(e))


@wallet.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.argument('name', required=True)
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.pass_obj
def init(shared_object: SharedObject, name: str, wait: bool):
    """
    Initialize address as a wallet
    """
    try:
        record = shared_object.keystore.get_record_by_name(name, raise_none=True)
    except RecordDoesNotExistError as e:
        raise CustomClickException(repr(e))

    address_info = shared_object.ton_client.get_address_information(record.address)

    if address_info.state == AddressState.active:
        raise CustomClickException("Wallet is already active.")

    if address_info.balance < (init_amount := WalletContract.init_amount(record.version)):
        raise CustomClickException(
            f"Insufficient amount, at least {init_amount} required.")

    try:
        wallet, _ = shared_object.keystore.get_wallet_from_record(record)
    except KeyStoreInvalidPasswordError as e:
        raise CustomClickException(repr(e))

    _, result = shared_object.ton_client.deploy_wallet(wallet, wait)

    click.echo(result)


@wallet.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_whitelist
@with_keystore(sensitive_data=True)
@click.argument('from_wallet', required=True, metavar='WALLET_NAME')
@click.argument('to_contact', required=True, metavar='CONTACT_NAME')
@click.argument('amount', required=False, metavar='TON_COINS_NUM')
@click.option('--contact', 'contact_type', default=None, show_default=True,
              type=click.Choice(PRETTY_CONTACT_TYPE_NAMES.keys()),
              help='Restrict the contact search to a specific whitelist')
@click.option('--message', '-m', help='Attach message to the transfer')
@click.option('--encrypt-message', '-e', 'encrypt_message_flag', help='Encrypt message', is_flag=True, default=False)
@click.option('--wait', '-w', is_flag=True, help='Wait until transaction is committed', default=False)
@click.option('--pay-gas-separately', default="y", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--ignore-errors', default="n", type=click.Choice(["y", "n"]), show_default=True,
              help='Bounce back if error occurs', callback=y_n_to_bool)
@click.option('--destroy-if-zero', default="n", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--transfer-all', default="n", type=click.Choice(["y", "n"]),
              show_default=True, callback=y_n_to_bool)
@click.option('--body', metavar='FILE', required=False, help="Path to a file containing the body (bag of cells)")
@click.option('--state-init', metavar='FILE', required=False,
              help='Path to a file containing the state init (bag of cells)')
@click.pass_obj
def transfer(shared_object: SharedObject, from_wallet, to_contact, contact_type, amount, message, encrypt_message_flag,
             wait, pay_gas_separately, ignore_errors, destroy_if_zero, transfer_all, body, state_init):
    """
    Transfer coins from your wallet to any address
    """
    if amount is None and not transfer_all:
        raise CustomClickException(
            "You must specify amount when you do not use --transfer-all flag.")

    if (message is not None) and (body is not None):
        raise CustomClickException("You cannot specify message and body at the same time.")

    if body is not None:
        try:
            with open(body, 'rb') as file_obj:
                body = file_obj.read()
        except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
            raise CustomClickException(f"Failed to open file: '{body}'")
        try:
            body = Cell.one_from_boc(body)
        except Exception:
            raise CustomClickException("Failed to parse body bag of cells")

    if state_init is not None:
        try:
            with open(state_init, 'rb') as file_obj:
                state_init = file_obj.read()
        except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
            raise CustomClickException(f"Failed to open file: '{state_init}'")
        try:
            state_init = Cell.one_from_boc(state_init)
        except Exception:
            raise CustomClickException("Failed to parse state init bag of cells")

    try:
        record = shared_object.keystore.get_record_by_name(
            from_wallet, raise_none=True)
        wallet, secret = shared_object.keystore.get_wallet_from_record(record)
        contact = get_contact(shared_object, to_contact, PRETTY_CONTACT_TYPE_NAMES.get(contact_type, None))
    except (
            WhitelistContactDoesNotExistError, RecordDoesNotExistError,
            KeyStoreInvalidPasswordError, WhitelistContactAmbiguityError) as e:
        raise CustomClickException(repr(e))

    send_mode = 0
    if ignore_errors:
        send_mode |= SendModeEnum.ignore_errors
    if pay_gas_separately:
        send_mode |= SendModeEnum.pay_gas_separately
    if destroy_if_zero:
        send_mode |= SendModeEnum.destroy_account_if_zero
    if transfer_all:
        send_mode |= SendModeEnum.carry_all_remaining_balance
        amount = 0

    if encrypt_message_flag:
        if not message:
            raise CustomClickException("Please specify message to encrypt (--message)")

        receiver_info = shared_object.ton_client.get_address_information(contact.address)
        if not receiver_info.is_wallet:
            raise CustomClickException("Contact cannot receive encrypted messages")

        message = encrypt_message(message, secret.public_key, receiver_info.public_key, secret.private_key,
                                  wallet.address)

    messages = [InternalMessage(
        to_addr=Address(contact.address),
        amount=amount,
        currency=TonCurrencyEnum.ton,
        body=message or body,
        state_init=state_init,
    )]

    _, result = shared_object.ton_client.transfer(wallet, messages, wait)
    click.echo(result)


@wallet.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_keystores
@with_keystore(sensitive_data=True)
@click.argument('wallet_name', type=str, required=True, )
@click.argument('keystore_name_dst', metavar='KEYSTORE_DST', type=str, required=True)
@click.option('--delete', '-d', 'remove_old', is_flag=True, default=False,
              help='Remove wallet from the current keystore')
@click.pass_obj
def move(ctx: SharedObject, wallet_name: str, keystore_name_dst: str, remove_old: bool):
    """
    Move wallet to another keystore
    """
    keystore_src = ctx.keystore

    try:
        record = keystore_src.get_record_by_name(wallet_name, raise_none=True)
    except RecordDoesNotExistError as e:
        raise CustomClickException(repr(e))

    try:
        keystore_dst = ctx.keystores.get_keystore(keystore_name_dst,
                                                  raise_none=True)
    except KeyStoreDoesNotExistError as e:
        raise CustomClickException(repr(e))

    if keystore_dst.has_been_upgraded:
        click.echo(keystore_upgrade_message(keystore_dst))

    secret = ctx.keystore.get_secret(record)
    try:
        if secret.mnemonics:
            keystore_dst.add_new_record(record.name, secret.mnemonics.split(), record.version, record.workchain,
                                        record.subwallet_id, record.comment, save=True)
        else:
            keystore_dst.add_new_record_from_pk(record.name, secret.private_key, record.version, record.workchain,
                                                record.subwallet_id, record.comment, save=True)
    except RecordAlreadyExistsError as e:
        raise CustomClickException(repr(e))

    if remove_old:
        ctx.keystore.delete_record(record.name, save=True)

    click_echo_success(f'Wallet \"{wallet_name}\" has been successfully {"moved" if remove_old else "copied"} '
                       f'from {keystore_src.name} to {keystore_dst.name}')
