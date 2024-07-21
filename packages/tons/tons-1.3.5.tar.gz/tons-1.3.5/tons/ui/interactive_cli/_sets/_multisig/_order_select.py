import enum
import typing as t

from tons.tonclient.utils import MultiSigOrderRecord
from tons.ui._utils import SharedObject
from tons.ui.interactive_cli._sets._multisig._mixin import MultiSigMixin
from tons.ui.interactive_cli._sets._multisig._order_relevance import OrderRelevanceBaseSet


class OrderRelevance(enum.Enum):
    active = enum.auto()
    history = enum.auto()
    all = enum.auto()


class _OrderSelectSet(OrderRelevanceBaseSet, MultiSigMixin):
    def __init__(self, ctx: SharedObject, message: str) -> None:
        super().__init__(ctx, message)
        self._selected_order: t.Optional[MultiSigOrderRecord] = None

    def _handle_relevant(self):
        self._selected_order = self._select_active_order()
        if self._selected_order is not None:
            self._handle_exit()

    def _handle_history(self):
        self._selected_order = self._select_inactive_order()
        if self._selected_order is not None:
            self._handle_exit()

    def _handle_all(self):
        self._selected_order = self._select_order()
        if self._selected_order is not None:
            self._handle_exit()

    def selected_order(self) -> t.Optional[MultiSigOrderRecord]:
        return self._selected_order


def select_order_with_relevance(ctx, message: str = "Pick from") -> t.Optional[MultiSigOrderRecord]:
    set_ = _OrderSelectSet(ctx, message)
    set_.show()
    return set_.selected_order()


