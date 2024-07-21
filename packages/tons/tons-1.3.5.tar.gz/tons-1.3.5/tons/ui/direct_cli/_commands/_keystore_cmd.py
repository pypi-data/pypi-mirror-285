import click

from tons import settings
from tons.tonclient.utils import KeyStoreAlreadyExistsError, KeyStoreInvalidPasswordError, \
    InvalidMnemonicsError
from tons.tonclient.utils._exceptions import InvalidBackupError
from tons.tonclient.utils._keystores import KeyStoreTypeEnum, PasswordKeyStore
from ._base_cmd import cli
from .._utils import CustomClickException, with_keystores, with_keystore, click_echo_success, keystore_upgrade_message
from ..._utils import SharedObject


@cli.group()
def keystore():
    """
    Operate with keystores
    """


@keystore.command()
@with_keystores
@click.argument('name', required=True)
@click.option('--keystore-type', '-t', default=KeyStoreTypeEnum.password.value, show_default=True,
              type=click.Choice([KeyStoreTypeEnum.password]))
@click.option("--password", default=settings.KEYSTORE_PASSWORD, show_default=False,
              help='Required only for a "password" type keystore')
@click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
              help='Required only for a "yubikey" type keystore')
@click.pass_obj
def new(shared_object: SharedObject, name, keystore_type, password, pin):
    """
    Create new .keystore file with a given name
    """
    try:
        if keystore_type == KeyStoreTypeEnum.password:
            if not password:
                password = click.prompt("Password[]", hide_input=True)
            shared_object.keystores.create_new_keystore(
                name, keystore_type, secret=password,
                save=True, )
        elif keystore_type == KeyStoreTypeEnum.yubikey:
            if not pin:
                pin = click.prompt("Yubikey PIN[]", hide_input=True)
            shared_object.keystores.create_new_keystore(
                name, keystore_type, secret=pin,
                save=True)
    except (
            KeyStoreAlreadyExistsError, KeyStoreInvalidPasswordError,
            Exception) as e:  # fixme: specify exceptions from yubikey
        raise CustomClickException(repr(e))

    click_echo_success(
        f"keystore {name} has been created. To use it run 'tons config tons.keystore_name {name}'.")


@keystore.command(name='list')
@with_keystores
@click.pass_obj
def list_(shared_object: SharedObject):
    """
    List all .keystore files in a current keystore workdir
    """
    keystores = shared_object.keystores.load_all()

    for keystore in keystores:
        if keystore.has_been_upgraded:
            click.echo(keystore_upgrade_message(keystore))
        click.echo(keystore.pretty_string())


@keystore.command()
@with_keystore(sensitive_data=True)
@with_keystores
@click.argument('backup_file_path', required=True, type=click.Path(writable=True))
@click.option('--yes', '-y', 'is_sure', is_flag=True, help='Do not show the prompt')
@click.pass_obj
def backup(shared_object: SharedObject, backup_file_path: str, is_sure: bool):
    """
    Backup the keystore into a specified file
    """
    if not is_sure:
        click.confirm(
            'Backup stores keys in UNENCRYPTED FORM. Are you sure want to export unencrypted keys to disk?',
            abort=True)
    try:
        shared_object.keystores.backup_keystore(
            shared_object.keystore, backup_file_path)
    except (KeyStoreInvalidPasswordError, OSError) as e:
        raise CustomClickException(repr(e))

    click_echo_success(
        f"backup {backup_file_path} has been created from the keystore {shared_object.config.tons.keystore_name}")


@keystore.command()
@with_keystores
@click.argument('name', required=True)
@click.argument('backup_file_path', required=True, type=click.Path(exists=True, readable=True))
@click.option('--keystore-type', '-t', default=KeyStoreTypeEnum.password.value, show_default=True,
              type=click.Choice([KeyStoreTypeEnum.password]))
@click.option("--password", default=settings.KEYSTORE_PASSWORD, show_default=False,
              help='Required only for a "password" type keystore')
@click.option("--pin", default=settings.YUBIKEY_PIN, show_default=False,
              help='Required only for a "yubikey" type keystore')
@click.option('--from-ton-cli', 'from_ton_cli', is_flag=True, help='Restore from the ton-cli util')
@click.pass_obj
def restore(shared_object: SharedObject, name: str, backup_file_path: str, keystore_type,
            password: str, pin: str, from_ton_cli: bool):
    """
    Restore the keystore from a specified file
    """
    try:
        if keystore_type == KeyStoreTypeEnum.password:
            if not password:
                password = click.prompt("Password[]", hide_input=True)
            PasswordKeyStore.validate_password(password)
            secret = password
        elif keystore_type == KeyStoreTypeEnum.yubikey:
            if not pin:
                pin = click.prompt("Yubikey PIN[]", hide_input=True)
            secret = pin
        else:
            raise CustomClickException("Unknown keystore type.")

        if from_ton_cli:
            shared_object.keystores.restore_ton_cli_keystore(
                name, backup_file_path, keystore_type, secret)
        else:
            shared_object.keystores.restore_tons_keystore(
                name, backup_file_path, keystore_type, secret)

    except (InvalidBackupError, InvalidMnemonicsError, KeyStoreAlreadyExistsError, KeyStoreInvalidPasswordError) as e:
        raise CustomClickException(repr(e))

    click_echo_success(f"keystore {name} has been restored.")
