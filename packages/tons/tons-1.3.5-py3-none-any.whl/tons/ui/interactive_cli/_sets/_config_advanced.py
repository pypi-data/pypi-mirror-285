from collections import OrderedDict

import inquirer

from tons import settings
from tons.config import TonNetworkEnum, set_network, update_config_field
from tons.ui._utils import SharedObject
from tons.ui.interactive_cli._modified_inquirer import terminal
from tons.ui.interactive_cli._sets._base import BaseSet, MenuItem
from tons.ui.interactive_cli._validators import number_greater_than_or_equal_to_zero
from .._utils import reinit_client_and_daemons


class AdvancedConfigSet(BaseSet):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self.config_path = settings.current_config_path()

    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}N{terminal.no_underline}etwork"] = \
            MenuItem(self._handle_network, "n")
        ord_dict[f'{terminal.underline}T{terminal.no_underline}estnet API key'] = \
            MenuItem(self._handle_tesnet_api_key, 't')
        ord_dict[f'DNS {terminal.underline}r{terminal.no_underline}efresh send amount'] = \
            MenuItem(self._handle_dns_refresh_send_amount, 'r')
        ord_dict[f'DNS {terminal.underline}c{terminal.no_underline}laim ownership send amount'] = \
            MenuItem(self._handle_dns_claim_ownership_send_amount, 'c')
        # ord_dict[f'{terminal.underline}J{terminal.no_underline}etton gas amount'] = \
        #     MenuItem(self._handle_jetton_gas_amount, 'j')
        ord_dict[f'{terminal.underline}M{terminal.no_underline}ultisig deploy amount'] = \
            MenuItem(self._handle_multisig_deploy_amount, 'm')
        ord_dict[f'{terminal.underline}P{terminal.no_underline}lace multisig order amount'] = \
            MenuItem(self._handle_order_deploy_amount, 'p')
        ord_dict[f"{terminal.underline}A{terminal.no_underline}pprove multisig order amount"] = \
            MenuItem(self._handle_order_approve_send_amount, 'a')
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_network(self):
        questions = [
            inquirer.List(
                "network", message='TON network to use', choices=[e.value for e in TonNetworkEnum],
                carousel=True, default=self.ctx.config.provider.dapp.network),
        ]
        network = TonNetworkEnum(self._prompt(questions)["network"])
        set_network(self.ctx.config, self.config_path, network)
        self.ctx.config.provider.dapp.network = network
        reinit_client_and_daemons(self.ctx)

    def _handle_tesnet_api_key(self):
        questions = [inquirer.Text('testnet_api_key',
                                   'Testnet API key',
                                   default=self.ctx.config.provider.dapp.testnet_api_key)]
        testnet_api_key = self._prompt(questions)['testnet_api_key']
        self.ctx.config.provider.dapp.testnet_api_key = testnet_api_key
        update_config_field(self.config_path,
                            'provider.dapp.testnet_api_key',
                            testnet_api_key)
        reinit_client_and_daemons(self.ctx)

    def _handle_dns_refresh_send_amount(self):
        questions = [inquirer.Text("refresh_send_amount",
                                   "DNS refresh send amount",
                                   default=self.ctx.config.dns.refresh_send_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        refresh_send_amount = self._prompt(questions)['refresh_send_amount']
        self.ctx.config.dns.refresh_send_amount = refresh_send_amount
        update_config_field(self.config_path, 'dns.refresh_send_amount', refresh_send_amount)
        reinit_client_and_daemons(self.ctx)

    def _handle_dns_claim_ownership_send_amount(self):
        questions = [inquirer.Text('refresh_not_yet_owned_send_amount',
                                   "DNS claim ownership send amount",
                                   default=self.ctx.config.dns.refresh_not_yet_owned_send_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        refresh_not_yet_owned_send_amount = self._prompt(questions)['refresh_not_yet_owned_send_amount']
        self.ctx.config.dns.refresh_not_yet_owned_send_amount = refresh_not_yet_owned_send_amount
        update_config_field(self.config_path,
                            'dns.refresh_not_yet_owned_send_amount',
                            refresh_not_yet_owned_send_amount)
        reinit_client_and_daemons(self.ctx)

    def _handle_jetton_gas_amount(self):
        questions = [inquirer.Text('gas_amount',
                                   'Jetton gas amount',
                                   default=self.ctx.config.jetton.gas_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        gas_amount = self._prompt(questions)['gas_amount']
        self.ctx.config.jetton.gas_amount = gas_amount
        update_config_field(self.config_path,
                            'jetton.gas_amount',
                            gas_amount)
        reinit_client_and_daemons(self.ctx)

    def _handle_multisig_deploy_amount(self):
        questions = [inquirer.Text('amount',
                                   'Multisig deploy amount',
                                   default=self.ctx.config.jetton.gas_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        amount = self._prompt(questions)['amount']
        self.ctx.config.jetton.gas_amount = amount
        update_config_field(self.config_path,
                            'multisig.multisig_deploy_amount',
                            amount)
        reinit_client_and_daemons(self.ctx)

    def _handle_order_deploy_amount(self):
        questions = [inquirer.Text('amount',
                                   'Place multisig order amount',
                                   default=self.ctx.config.jetton.gas_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        amount = self._prompt(questions)['amount']
        self.ctx.config.jetton.gas_amount = amount
        update_config_field(self.config_path,
                            'multisig.order_deploy_amount',
                            amount)
        reinit_client_and_daemons(self.ctx)

    def _handle_order_approve_send_amount(self):
        questions = [inquirer.Text('amount',
                                   'Approve multisig order amount',
                                   default=self.ctx.config.jetton.gas_amount,
                                   validate=number_greater_than_or_equal_to_zero)]
        amount = self._prompt(questions)['amount']
        self.ctx.config.jetton.gas_amount = amount
        update_config_field(self.config_path,
                            'multisig.order_approve_send_amount',
                            amount)
        reinit_client_and_daemons(self.ctx)


