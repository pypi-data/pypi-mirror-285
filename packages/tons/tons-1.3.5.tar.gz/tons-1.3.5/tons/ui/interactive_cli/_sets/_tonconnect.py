from base64 import b64decode
from collections import OrderedDict
from typing import OrderedDict as OrderedDictTyping, Tuple, Optional

import click
import inquirer
from inquirer import Text
from nacl.public import PrivateKey

from tons import settings
from tons.tonclient.utils._tonconnect import initiate_connect_event, TonconnectConnection, initiate_disconnect_event, \
    get_new_request
from tons.tonclient.utils._tonconnect._handlers import accept_request, decline_request
from tons.tonsdk.utils.tonconnect import Session
from tons.tonsdk.utils.tonconnect._bridge import Bridge
from ._base import BaseSet, MenuItem
from ._mixin import KeyStoreMixin, keystore_sensitive_area
from .._modified_inquirer import terminal, ListWithFilter
from .._utils import echo_success, processing
from ..._utils import SharedObject, form_tonconnect_table, form_request_info, TxAction


class TonconnectSet(BaseSet, KeyStoreMixin):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick Tonconnect command [{self.ctx.keystore.name}]"

    def _handlers(self) -> OrderedDictTyping[str, MenuItem]:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}H{terminal.no_underline}andle requests"] = \
            MenuItem(self._handle_requests, "h")
        ord_dict[f"{terminal.underline}N{terminal.no_underline}ew connection"] = \
            MenuItem(self._handle_connect, "n")
        ord_dict[f"{terminal.underline}L{terminal.no_underline}ist connections"] = \
            MenuItem(self._handle_list, "l")
        ord_dict[f"{terminal.underline}D{terminal.no_underline}isconnect"] = \
            MenuItem(self._handle_disconnect, "d")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_requests(self):
        if not self.ctx.keystore.connections:
            echo_success("No connections yet.")
            return

        self.__handle_requests()

    @keystore_sensitive_area
    def __handle_requests(self):
        found_connection = None
        bridge = Bridge(settings.BRIDGE_HOST, settings.BRIDGE_PORT, settings.BRIDGE_URL)
        while True:
            while found_connection is None:
                with processing("waiting for new requests"):
                    for connection in self.ctx.keystore.connections:
                        session = Session(private_key=PrivateKey(
                            self.ctx.keystore.tonconnector.decrypt_priv_key(connection.encrypted_priv_key)),
                            app_public_key=Session.public_key_from_hex(connection.dapp_client_id))
                        try:
                            tx_request, event_id = get_new_request(self.ctx.keystore, connection.wallet_name,
                                                                   connection.dapp_client_id,
                                                                   connection, session, bridge,
                                                                   self.ctx.config.provider.dapp.network, 1)
                            found_connection = connection
                        except TimeoutError:
                            # echo_success(f"No requests found for {connection.wallet_name}.")
                            continue

            click.echo(self.__prettify_connection_info(found_connection))
            click.echo(form_request_info(tx_request))
            action = self._prompt([
                inquirer.List(
                    "action", message="Select an action", choices=[str(choice.value) for choice in TxAction],
                    carousel=True), ])["action"]

            if action == TxAction.confirm:
                with processing():
                    accept_request(self.ctx.keystore, found_connection.wallet_name, found_connection.dapp_client_id,
                                   event_id, tx_request, self.ctx.ton_client, session, bridge)
                echo_success('Confirmed successfully.')

            else:
                with processing():
                    decline_request(self.ctx.keystore, found_connection.wallet_name, found_connection.dapp_client_id,
                                    event_id, tx_request.id, session, bridge)
                echo_success('Canceled successfully.')

            found_connection = None

    def _handle_connect(self):
        wallet_name = self.select_wallet("Connect wallet", verbose=True)
        if wallet_name is None:
            return

        base64_universal_link = self._prompt([Text("base64_universal_link", message="Connection payload")])[
            "base64_universal_link"]

        self.__initiate_connect_event(wallet_name, base64_universal_link)

        echo_success(f'Wallet {wallet_name} has been connected.')

    @keystore_sensitive_area
    def __initiate_connect_event(self, wallet_name: str, base64_universal_link: str):
        initiate_connect_event(self.ctx.config, self.ctx.keystore, wallet_name,
                               b64decode(base64_universal_link).decode())

    def _handle_list(self):
        table = form_tonconnect_table(self.ctx.keystore.connections)
        echo_success(table, only_msg=True)

    def _handle_disconnect(self):
        wallet_name, dapp_client_id = self.__select_connection()
        if wallet_name is None:
            return

        self.__initiate_disconnect_event(wallet_name, dapp_client_id)

        echo_success(f'Wallet {wallet_name} has been disconnected.')

    @keystore_sensitive_area
    def __initiate_disconnect_event(self, wallet_name: str, dapp_client_id: str):
        initiate_disconnect_event(self.ctx.keystore, wallet_name, dapp_client_id)

    def __select_connection(self) -> Tuple[Optional[str], Optional[str]]:
        if not self.ctx.keystore.connections:
            echo_success("You do not have any connections yet.")
            return None, None

        questions = [
            ListWithFilter(
                "wallet",
                message="Select Connection",
                choices=ListWithFilter.zip_choices_and_values([self.__prettify_connection_info(connection)
                                                               for connection in self.ctx.keystore.connections],
                                                              self.ctx.keystore.connections),
                carousel=True,
            )
        ]
        connection = self._prompt(questions)["wallet"]
        return connection.wallet_name, connection.dapp_client_id

    @staticmethod
    def __prettify_connection_info(connection: TonconnectConnection) -> str:
        return f"Between '{connection.wallet_name}' wallet and '{connection.app_manifest.name}' " \
               f"dapp (client id: {connection.dapp_client_id})"
