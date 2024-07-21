import base64
import json
import time
from typing import Union
from urllib.parse import urlparse, parse_qsl

import requests
from nacl.public import PrivateKey
from nacl.utils import EncryptedMessage

import tons.version
from tons import settings
from tons.config import TonNetworkEnum
from tons.tonsdk.boc import Cell
from tons.tonsdk.contract.wallet import Wallets, InternalMessage
from tons.tonsdk.utils import bytes_to_b64str, TonCurrencyEnum, b64str_to_bytes, Address
from tons.tonsdk.utils.tonconnect import Session
from tons.tonsdk.utils.tonconnect._bridge import Bridge
from tons.tonsdk.utils.tonconnect.requests_responses import AppManifest, DeviceInfo, ConnectRequest, \
    TonConnectItemEnum, TonAddressItemReply, TonconnectNetworkEnum, ConnectEventSuccessPayload, ConnectEventSuccess, \
    DisconnectEvent, SendTransactionRequest, WalletResponseSuccess, WalletResponseError, WalletResponseErrorPayload, \
    SendTransactionResponseErrorCodeEnum, AppRequestMethodEnum
from ._models import TonconnectConnection
from ._utils import UniversalLink, get_network
from .._exceptions import TonconnectUnsupportedMethodError, TonconnectBadRequestError, \
    TonconnectDifferentNetworkError, TonconnectWrongMessagesNumberError, TonconnectWrongParamsNumberError, \
    TonconnectWrongRpcRequestIdError, TonconnectRequestExpiredError
from .._keystores._keystore._secret import WalletSecretKind
from ... import TonClient


def initiate_connect_event(config, keystore: 'BaseKeyStore', wallet_name, universal_link):
    wallet_record = keystore.get_record_by_name(wallet_name, raise_none=True)
    pub_k, wallet = _get_wallet_and_pubk(keystore, wallet_record)

    parsed_url = urlparse(universal_link)
    universal_link = UniversalLink.parse_obj(dict(parse_qsl(parsed_url.query)))
    connect_request = ConnectRequest.parse_obj(json.loads(universal_link.r))
    app_manifest = AppManifest.parse_obj(requests.get(connect_request.manifestUrl).json())

    if len(connect_request.items) != 1 or connect_request.items[0].name != TonConnectItemEnum.ton_addr:
        raise NotImplementedError("Only ton_addr request is implemented.")

    device = DeviceInfo(platform=DeviceInfo.find_platform(), appName='tons', appVersion=tons.version.__version__,
                        maxProtocolVersion=2, )
    # features=[SendTransactionFeature(maxMessages=1)])  # todo: uncomment when tonconnect-sdk supports this feature

    network = TonconnectNetworkEnum.mainnet \
        if config.provider.dapp.network == "mainnet" \
        else TonconnectNetworkEnum.testnet
    ton_addr_item_reply = TonAddressItemReply(
        address=wallet.address.to_string(False), network=network, publicKey=pub_k.hex(),
        walletStateInit=bytes_to_b64str(wallet.create_state_init()["state_init"].to_boc(False)))

    connect_success = ConnectEventSuccess(id=0, payload=ConnectEventSuccessPayload(items=[ton_addr_item_reply],
                                                                                   device=device))

    session = Session(app_public_key=Session.public_key_from_hex(universal_link.id))
    encrypted_message = session.encrypt_msg(json.dumps(connect_success.dict()))
    data = base64.b64encode(encrypted_message).decode()
    bridge = Bridge(settings.BRIDGE_HOST, settings.BRIDGE_PORT, settings.BRIDGE_URL)
    bridge.send_message(session.session_id, Session.public_key_to_hex(session.app_public_key),
                        data, raise_status_code=True)

    keystore.tonconnector.add(session.private_key, universal_link.id, 0, 0, 0, wallet_name, app_manifest, save=True)


def initiate_disconnect_event(keystore, wallet_name, dapp_client_id):
    connection, session, bridge = find_connection(keystore, wallet_name, dapp_client_id)
    disconnect_event = DisconnectEvent(id=connection.next_wallet_event_id)
    encrypted_message = session.encrypt_msg(json.dumps(disconnect_event.dict()))
    data = base64.b64encode(encrypted_message).decode()

    bridge.send_message(session.session_id, Session.public_key_to_hex(session.app_public_key),
                        data, raise_status_code=True)
    keystore.tonconnector.delete(wallet_name, dapp_client_id, save=True)


def get_new_request(keystore, wallet_name, dapp_client_id, connection, session, bridge,
                    current_network: TonNetworkEnum, timeout: int = 60) -> (
        SendTransactionRequest, int):
    data, event_id = bridge.get_event(session.session_id, connection.last_bridge_event_id, timeout)
    assert data.from_ == connection.dapp_client_id
    assert int(event_id) > connection.last_bridge_event_id

    decrypted_msg = json.loads(session.decrypt_msg(EncryptedMessage(base64.b64decode(data.message))))
    decrypted_msg['params'] = [json.loads(param) for param in decrypted_msg['params']]

    send_tx_request, error_code, exc = None, None, None
    try:
        send_tx_request = SendTransactionRequest.parse_obj(decrypted_msg)
    except ValueError:
        error_code = SendTransactionResponseErrorCodeEnum.bad_request
        exc = TonconnectBadRequestError("Dapp sent bad request.")
        if 'method' in decrypted_msg and decrypted_msg['method'] != AppRequestMethodEnum.send_transaction:
            error_code = SendTransactionResponseErrorCodeEnum.method_not_supported
            exc = TonconnectUnsupportedMethodError(
                f"Request with a method '{decrypted_msg.get('method', None)}' is not supported yet.")
    else:
        if any((get_network(param) != current_network for param in send_tx_request.params)):
            exc = TonconnectDifferentNetworkError("Dapp requested sending transaction in different network. "
                                                  "Note: you may change network in the config.")
            error_code = SendTransactionResponseErrorCodeEnum.bad_request
        elif not all(1 <= len(param.messages) <= 4 for param in send_tx_request.params):
            exc = TonconnectWrongMessagesNumberError("Dapp requested sending wrong number of messages.")
            error_code = SendTransactionResponseErrorCodeEnum.bad_request
        elif len(send_tx_request.params) != 1:
            exc = TonconnectWrongParamsNumberError(
                f"Dapp requested wrong number of params ({len(send_tx_request.params)}).")
            error_code = SendTransactionResponseErrorCodeEnum.bad_request
    finally:
        try:
            msg_rpc_request_id = int(decrypted_msg.get('id', connection.last_rpc_event_id))
        except ValueError:
            msg_rpc_request_id = 0
        time_now = int(time.time() * 1000)

        if not error_code \
                and not exc \
                and (msg_rpc_request_id <= connection.last_rpc_event_id) \
                and connection.last_rpc_event_id != 0:
            exc = TonconnectWrongRpcRequestIdError(
                f"Dapp sent wrong rpc event id: {msg_rpc_request_id}; "
                f"current is {connection.last_rpc_event_id}.")
            error_code = SendTransactionResponseErrorCodeEnum.bad_request
        elif any([param.valid_until <= time_now for param in send_tx_request.params]):
            exc = TonconnectRequestExpiredError(
                f"Dapp sent a request that has been expired.")
            error_code = SendTransactionResponseErrorCodeEnum.bad_request

        if error_code and exc:
            error_payload = WalletResponseErrorPayload(code=error_code)
            wallet_response_error = WalletResponseError(error=error_payload, id=msg_rpc_request_id)
            encrypted_message = session.encrypt_msg(json.dumps(wallet_response_error.dict()))
            data = base64.b64encode(encrypted_message).decode()
            bridge.send_message(session.session_id, Session.public_key_to_hex(session.app_public_key),
                                data, raise_status_code=True)
            rpc_req_id = msg_rpc_request_id \
                if msg_rpc_request_id > connection.last_rpc_event_id \
                else connection.last_rpc_event_id
            keystore.tonconnector.update(wallet_name, dapp_client_id, new_bridge_event_id=event_id,
                                         new_rpc_event_id=rpc_req_id, save=True)

            raise exc

        return send_tx_request, event_id


def find_connection(keystore, wallet_name, dapp_client_id) -> (TonconnectConnection, Session, Bridge):
    connection = keystore.tonconnector.get(wallet_name, dapp_client_id, raise_none=True)
    session = Session(private_key=PrivateKey(keystore.tonconnector.decrypt_priv_key(connection.encrypted_priv_key)),
                      app_public_key=Session.public_key_from_hex(connection.dapp_client_id))

    bridge = Bridge(settings.BRIDGE_HOST, settings.BRIDGE_PORT, settings.BRIDGE_URL)

    return connection, session, bridge


def accept_request(keystore, wallet_name, dapp_client_id, event_id, request: Union[SendTransactionRequest],
                   ton_client: TonClient, session: Session, bridge: Bridge):
    wallet_record = keystore.get_record_by_name(wallet_name, raise_none=True)
    pub_k, wallet = _get_wallet_and_pubk(keystore, wallet_record)

    # https://github.com/ton-blockchain/ton-connect/blob/main/requests-responses.md#structure
    # handle only one parameter for now because there is no way to respond to more than one
    param = request.params[0]
    messages = []
    for message in param.messages:
        body = message.payload
        state_init = message.stateInit
        if state_init is not None:
            state_init = Cell.one_from_boc(b64str_to_bytes(state_init))
        if body is not None:
            body = Cell.one_from_boc(b64str_to_bytes(body))
        messages.append(InternalMessage(
            to_addr=Address(message.address),
            amount=int(message.amount),
            currency=TonCurrencyEnum.nanoton,
            body=body,
            state_init=state_init,
        ))

    wait = True
    query, result = ton_client.transfer(wallet, messages, wait)

    wallet_response_success = WalletResponseSuccess(result=bytes_to_b64str(query['message'].to_boc(False)),
                                                    id=request.id)

    encrypted_message = session.encrypt_msg(json.dumps(wallet_response_success.dict()))
    data = base64.b64encode(encrypted_message).decode()
    bridge.send_message(session.session_id, Session.public_key_to_hex(session.app_public_key),
                        data, raise_status_code=True)

    keystore.tonconnector.update(wallet_name, dapp_client_id, new_bridge_event_id=event_id,
                                 new_rpc_event_id=request.id, save=True)


def _get_wallet_and_pubk(keystore, wallet_record):
    secret = keystore.get_secret(wallet_record)
    if secret.kind == WalletSecretKind.mnemonics:
        # todo test & refactor, the "else" section should work just as this section
        mnemonics = secret.mnemonics.split(" ")
        _mnemonics, pub_k, _priv_k, wallet = Wallets.from_mnemonics(mnemonics, wallet_record.version,
                                                                    wallet_record.workchain, wallet_record.subwallet_id)
    else:
        wallet, secret = keystore.get_wallet_from_record(wallet_record)
        pub_k = secret.public_key
    return pub_k, wallet


def decline_request(keystore, wallet_name, dapp_client_id, event_id, rpc_request_id, session, bridge):
    error_payload = WalletResponseErrorPayload(code=SendTransactionResponseErrorCodeEnum.user_declined_the_connection)
    wallet_response_error = WalletResponseError(error=error_payload, id=rpc_request_id)

    encrypted_message = session.encrypt_msg(json.dumps(wallet_response_error.dict()))
    data = base64.b64encode(encrypted_message).decode()
    bridge.send_message(session.session_id, Session.public_key_to_hex(session.app_public_key),
                        data, raise_status_code=True)

    keystore.tonconnector.update(wallet_name, dapp_client_id, new_bridge_event_id=event_id,
                                 new_rpc_event_id=rpc_request_id, save=True)
