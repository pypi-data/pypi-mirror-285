import typing as t
from collections import OrderedDict

from ._orders import MultiSigOrderSet
from ._utils import add_menu_item
from .._base import BaseSet, MenuItem
from .._mixin import KeyStoreMixin
from ...._utils import SharedObject
from ._wallets import MultiSigWalletSet


class MultiSigSet(BaseSet):
    def __init__(self, ctx: SharedObject) -> None:
        super().__init__(ctx)
        self._menu_message = f"Pick multisig command [{self.ctx.keystore.name}]"

    def _handlers(self) -> t.OrderedDict[str, MenuItem]:
        ord_dict = OrderedDict()
        add_menu_item(ord_dict, "Wallet", 'w', self._handle_wallets)
        add_menu_item(ord_dict, "Order", 'o', self._handle_orders)
        add_menu_item(ord_dict, "Back", 'b', self._handle_exit)
        return ord_dict

    def _handle_wallets(self):
        MultiSigWalletSet(self.ctx).show()

    def _handle_orders(self):
        MultiSigOrderSet(self.ctx).show()

