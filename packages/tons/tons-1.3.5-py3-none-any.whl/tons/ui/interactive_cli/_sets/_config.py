from collections import OrderedDict

import inquirer

from tons import settings
from tons.config import update_config_field
from ._base import BaseSet, MenuItem
from ._config_advanced import AdvancedConfigSet
from .._modified_inquirer import ModifiedConfirm, terminal
from .._utils import echo_success, reinit_client_and_daemons
from .._validators import valid_dns_refresh_amount
from ..._utils import SharedObject


class ConfigSet(BaseSet):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self.config_path = settings.current_config_path()

    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}A{terminal.no_underline}PI key"] = \
            MenuItem(self._handle_api_key, "a")
        ord_dict[f"{terminal.underline}W{terminal.no_underline}orkdir"] = \
            MenuItem(self._handle_workdir, "w")
        ord_dict[f"{terminal.underline}S{terminal.no_underline}ort whitelist"] = \
            MenuItem(self._handle_sort_whitelist, "s")
        ord_dict[f"S{terminal.underline}o{terminal.no_underline}rt keystore"] = \
            MenuItem(self._handle_sort_keystore, "o")
        ord_dict[f"{terminal.underline}D{terminal.no_underline}NS expiration threshold"] = \
            MenuItem(self._handle_dns_expiring_in, 'd')
        ord_dict[f"Ad{terminal.underline}v{terminal.no_underline}anced"] = \
            MenuItem(self._handle_advanced, "v")
        ord_dict[f"{terminal.underline}C{terminal.no_underline}urrent setup"] = \
            MenuItem(self._handle_current_setup, "c")
        ord_dict[f"{terminal.underline}B{terminal.no_underline}ack"] = \
            MenuItem(self._handle_exit, "b")
        return ord_dict

    def _handle_api_key(self):
        questions = [
            inquirer.Text(
                "api_key", message='API key to access dapp',
                default=self.ctx.config.provider.dapp.__dict__['api_key']),
        ]
        api_key = self._prompt(questions)["api_key"]
        update_config_field(self.config_path, "provider.dapp.api_key", api_key)
        self.ctx.config.provider.dapp.api_key = api_key
        reinit_client_and_daemons(self.ctx)

    def _handle_workdir(self):
        questions = [
            inquirer.Path(
                "workdir", message='Working directory path (for whitelist and keystores)',
                default=self.ctx.config.tons.workdir, exists=True, path_type=inquirer.Path.DIRECTORY),
        ]
        workdir = self._prompt(questions)["workdir"]
        update_config_field(self.config_path, "tons.workdir", workdir)
        self.ctx.config.tons.workdir = workdir
        reinit_client_and_daemons(self.ctx)

    def _handle_sort_whitelist(self):
        self.__handle_sort_lists('Sort whitelist contacts automatically?',
                                 self.ctx.config.tons.sort_whitelist, "sort_whitelist")

    def _handle_sort_keystore(self):
        self.__handle_sort_lists('Sort keystore records automatically?',
                                 self.ctx.config.tons.sort_keystore, "sort_keystore")

    def _handle_dns_expiring_in(self):
        max_expiring_in = self._prompt([
            inquirer.Text('max_expiring_in',
                          message='DNS max expiring in (months)',
                          default=self.ctx.config.dns.max_expiring_in,
                          validate=valid_dns_refresh_amount)
        ])['max_expiring_in']
        self.ctx.config.dns.max_expiring_in = max_expiring_in
        update_config_field(self.config_path, "dns.max_expiring_in", max_expiring_in)

    def _handle_advanced(self):
        AdvancedConfigSet(self.ctx).show()

    def _handle_current_setup(self):
        for key, val in self.ctx.config.key_value():
            echo_success(f"{key}={val}", True)

    def __handle_sort_lists(self, msg, default, field_name):
        questions = [
            ModifiedConfirm(
                "sort_lists", message=msg,
                default=default),
        ]
        sort_lists = self._prompt(questions)["sort_lists"]
        update_config_field(self.config_path, f"tons.{field_name}", sort_lists)
        setattr(self.ctx.config.tons, field_name, sort_lists)
