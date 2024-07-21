from base64 import b64decode

import click
from requests import RequestException

from tons import settings
from tons.tonclient.utils import RecordDoesNotExistError
from tons.tonclient.utils._exceptions import ConnectionAlreadyExistsError, KeyStoreInvalidPasswordError
from tons.tonclient.utils._tonconnect import get_new_request, initiate_connect_event, initiate_disconnect_event, \
    find_connection
from tons.tonclient.utils._tonconnect._handlers import accept_request, decline_request
from ._base_cmd import cli
from .._utils import with_keystore, CustomClickException, click_echo_success
from ..._utils import SharedObject, form_tonconnect_table, form_request_info, TxAction


@cli.group()
def tonconnect():
    """
    Operate with TonConnect
    """


@tonconnect.command()
@with_keystore(sensitive_data=True)
@click.argument('wallet_name', required=True)
@click.argument('base64_universal_link', required=True)
@click.pass_obj
def connect(shared_object: SharedObject, wallet_name: str, base64_universal_link: str):
    try:
        initiate_connect_event(shared_object.config, shared_object.keystore, wallet_name,
                               b64decode(base64_universal_link).decode())
        click_echo_success(f'Wallet {wallet_name} has been connected.')

    except (RecordDoesNotExistError, RequestException, ConnectionAlreadyExistsError, KeyStoreInvalidPasswordError) as e:
        raise CustomClickException(repr(e))


@tonconnect.command(name='list')
@with_keystore(sensitive_data=False)
@click.pass_obj
def list_(shared_object: SharedObject):
    table = form_tonconnect_table(shared_object.keystore.connections)
    click.echo(table)


@tonconnect.command()
@with_keystore(sensitive_data=True)
@click.argument('wallet_name', required=True)
@click.argument('dapp_client_id', required=True)
@click.pass_obj
def disconnect(shared_object: SharedObject, wallet_name: str, dapp_client_id: str):
    try:
        initiate_disconnect_event(shared_object.keystore, wallet_name, dapp_client_id)
        click_echo_success(f'Wallet {wallet_name} has been disconnected.')

    except (RecordDoesNotExistError, RequestException, ConnectionAlreadyExistsError, KeyStoreInvalidPasswordError) as e:
        raise CustomClickException(repr(e))


@tonconnect.command()
@with_keystore(sensitive_data=True)
@click.argument('wallet_name', required=True)
@click.argument('dapp_client_id', required=True)
@click.pass_obj
def handle_queued_request(shared_object: SharedObject, wallet_name: str, dapp_client_id: str):
    try:
        connection, session, bridge = find_connection(shared_object.keystore, wallet_name, dapp_client_id)
        tx_request, event_id = get_new_request(shared_object.keystore, wallet_name, dapp_client_id, connection, session,
                                               bridge, shared_object.config.provider.dapp.network,
                                               settings.BRIDGE_WAIT_NEW_REQUEST_SEC)

    except RecordDoesNotExistError as e:
        raise CustomClickException(repr(e))

    except TimeoutError:
        click_echo_success("No queued requests found.")
        return

    click.echo(form_request_info(tx_request))
    action = click.prompt("Select an action [Confirm/Cancel]", type=TxAction, show_choices=True)

    if action == TxAction.confirm:
        accept_request(shared_object.keystore, wallet_name, dapp_client_id, event_id, tx_request,
                       shared_object.ton_client, session, bridge)
        click_echo_success('Confirmed successfully.')

    else:
        decline_request(shared_object.keystore, wallet_name, dapp_client_id, event_id, tx_request.id, session, bridge)
        click_echo_success('Canceled successfully.')
