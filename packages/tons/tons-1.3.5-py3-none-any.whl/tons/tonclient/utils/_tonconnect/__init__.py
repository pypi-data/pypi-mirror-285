from base64 import b64encode, b64decode
from copy import deepcopy
from typing import List, Optional, Union

from nacl.public import PrivateKey

from tons.tonsdk.utils.tonconnect.requests_responses import AppManifest
from ._handlers import initiate_connect_event, initiate_disconnect_event, get_new_request, find_connection
from ._models import TonconnectConnection
from ._utils import SupportedTonconnectVersionEnum, UniversalLink
from .._exceptions import ConnectionAlreadyExistsError, ConnectionDoesNotExistError, \
    RecordWithNameAlreadyExistsError


class Tonconnector:
    def __init__(self, connections: List[TonconnectConnection], keystore: 'BaseKeyStore'):
        self.connections = connections
        self.keystore = keystore

    def add(self, priv_key: PrivateKey, dapp_client_id: str, last_bridge_event_id: int, last_wallet_event_id: int,
            last_rpc_event_id: int, wallet_name: str, app_manifest: AppManifest, save: bool = False):
        if any([connection.dapp_client_id == dapp_client_id and connection.wallet_name == wallet_name
                for connection in self.connections]):
            raise ConnectionAlreadyExistsError(f"Connection with the client_id '{dapp_client_id}' "
                                               f"and wallet name '{wallet_name}' already exists")

        new_connection = TonconnectConnection(
            encrypted_priv_key=self.encrypt_priv_key(priv_key),
            dapp_client_id=dapp_client_id,
            last_bridge_event_id=last_bridge_event_id,
            last_wallet_event_id=last_wallet_event_id,
            last_rpc_event_id=last_rpc_event_id,
            wallet_name=wallet_name,
            app_manifest=app_manifest
        )

        with self.keystore.restore_on_failure():
            self.connections.append(new_connection)
            if save:
                self.keystore.save()

    def delete_all_by_name(self, wallet_name: str, save: bool = False):
        to_delete = [conn for conn in self.connections if conn.wallet_name == wallet_name]
        for conn in to_delete:
            self.delete(conn.wallet_name, conn.dapp_client_id, save)

    def delete(self, wallet_name: str, dapp_client_id: str, save: bool = False):
        connection = self.get(wallet_name, dapp_client_id, raise_none=True)
        with self.keystore.restore_on_failure():
            self.connections.remove(connection)
            if save:
                self.keystore.save()

        return connection

    def get(self, wallet_name: str, dapp_client_id: str, raise_none: bool = False) -> Optional[TonconnectConnection]:
        found_connection = next((connection for connection in self.connections if
                                 connection.dapp_client_id == dapp_client_id and connection.wallet_name == wallet_name),
                                None)

        if found_connection is None and raise_none:
            raise ConnectionDoesNotExistError(f"Connection with the client_id '{dapp_client_id}' "
                                              f"and wallet name '{wallet_name}' does not exist")

        return found_connection

    def update_wallet_name(self, old_name: str, new_name: str, save: bool = False):
        if next((conn for conn in self.connections if conn.wallet_name == new_name), None) is not None:
            raise ConnectionAlreadyExistsError(
                f"Connection with the wallet name '{new_name}' already exists")

        if new_name == '':
            raise ValueError('Wallet name should not be empty')

        with self.keystore.restore_on_failure():
            for connection in self.connections:
                if connection.wallet_name == old_name:
                    connection.wallet_name = new_name

            if save:
                self.keystore.save()

    def update(self, wallet_name: str, dapp_client_id: str, new_bridge_event_id: Optional[Union[int, str]] = None,
               new_wallet_event_id: Optional[Union[int, str]] = None,
               new_rpc_event_id: Optional[Union[int, str]] = None, save: bool = False):
        connection = self.get(wallet_name, dapp_client_id, raise_none=True)
        connection_idx = self.connections.index(connection)

        with self.keystore.restore_on_failure():
            if new_bridge_event_id is not None:
                self.connections[connection_idx].last_bridge_event_id = int(new_bridge_event_id)

            if new_wallet_event_id is not None:
                self.connections[connection_idx].last_wallet_event_id = int(new_wallet_event_id)

            if new_rpc_event_id is not None:
                self.connections[connection_idx].last_rpc_event_id = int(new_rpc_event_id)

            if save:
                self.keystore.save()

    def encrypt_priv_key(self, priv_key: PrivateKey) -> str:
        return b64encode(self.keystore.encrypt_secret(priv_key.encode())).decode("utf-8")

    def decrypt_priv_key(self, encrypted_priv_key: str) -> bytes:
        return self.keystore.decrypt_secret(b64decode(encrypted_priv_key))


__all__ = [
    "Tonconnector",
    "TonconnectConnection",
    "initiate_disconnect_event",
    "initiate_connect_event",
    "get_new_request",
    "find_connection",
    "UniversalLink",
    "SupportedTonconnectVersionEnum",
]
