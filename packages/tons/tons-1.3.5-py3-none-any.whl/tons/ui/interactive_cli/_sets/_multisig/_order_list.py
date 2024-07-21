import typing as t

from tons.tonclient.utils._multisig import BaseMultiSigRecord
from tons.ui._utils import form_multisig_order_table, SharedObject
from ._mixin import MultiSigMixin
from ._order_relevance import OrderRelevanceBaseSet
from ..._utils import processing, echo_success


MultiSigRecordFilter = t.Callable[[BaseMultiSigRecord], bool]


class OrderListSet(OrderRelevanceBaseSet, MultiSigMixin):
    def __init__(self, ctx: SharedObject, message: str = "List orders from"):
        super().__init__(ctx, message)
        self._menu_message = f"{message}"

    def _handle_relevant(self):
        self._handle_list(self._order_relevance_getter())
        self._handle_exit()

    def _handle_history(self):
        self._handle_list(self._order_irrelevance_getter())
        self._handle_exit()

    def _handle_all(self):
        self._handle_list()
        self._handle_exit()

    def _handle_list(self, filter_: t.Optional[MultiSigRecordFilter] = None):
        records = self._multisig_order_list().get_records()
        if filter_ is not None:
            records = tuple(filter(filter_, records))
        addresses = [r.address for r in records]
        with processing():
            addresses_info, orders_info = self.ctx.ton_client.get_multisig_orders_information(addresses)

        t = form_multisig_order_table(records, orders_info, addresses_info)
        echo_success(str(t), only_msg=True)
