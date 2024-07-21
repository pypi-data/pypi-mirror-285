from collections import OrderedDict

from tons.tonclient.utils import GlobalWhitelist
from tons.version import __version__ as tons_version
from ._base import BaseSet, MenuItem
from ._config import ConfigSet
from ._keystores import KeystoresSet
from ._whitelist import WhitelistSet, echo_success
from .._modified_inquirer import terminal


class EntrypointSet(BaseSet):
    def _handlers(self) -> OrderedDict:
        ord_dict = OrderedDict()
        ord_dict[f"{terminal.underline}K{terminal.no_underline}eystores"] = \
            MenuItem(self._handle_keystores, "k")
        ord_dict[f"{terminal.underline}W{terminal.no_underline}hitelist (global)"] = \
            MenuItem(self._handle_whitelist, "w")
        ord_dict[f"{terminal.underline}C{terminal.no_underline}onfig"] = \
            MenuItem(self._handle_config, "c")
        ord_dict[f"{terminal.underline}A{terminal.no_underline}bout"] = \
            MenuItem(self._handle_about, "a")
        ord_dict[f"{terminal.underline}E{terminal.no_underline}xit"] = \
            MenuItem(self._handle_exit, "e")
        return ord_dict

    def _handle_keystores(self):
        KeystoresSet(self.ctx).show()

    def _handle_whitelist(self):
        whitelist = GlobalWhitelist(self.ctx.config.tons.whitelist_path)
        WhitelistSet(self.ctx, whitelist, "global").show()

    def _handle_config(self):
        ConfigSet(self.ctx).show()

    def _handle_about(self):
        echo_success(f"""
tons v{tons_version}

Interface:
↑ ↓          - navigation
Enter        - proceed
Ctrl + C     - exit current command or navigate back
Esc + Esc    - exit current command or navigate back

Documentation:  {"https://tonfactory.github.io/tons-docs/"}
Support:        {"https://t.me/tonfactorychat"}
""", only_msg=True)
