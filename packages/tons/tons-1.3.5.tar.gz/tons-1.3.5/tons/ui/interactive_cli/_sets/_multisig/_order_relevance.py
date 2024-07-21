import enum
import typing as t
from abc import ABC, abstractmethod
from collections import OrderedDict

from tons.ui._utils import SharedObject
from tons.ui.interactive_cli._sets._base import BaseSet, MenuItem
from tons.ui.interactive_cli._sets._multisig._utils import add_menu_item


class OrderRelevance(enum.Enum):
    active = enum.auto()
    history = enum.auto()
    all = enum.auto()


class OrderRelevanceBaseSet(BaseSet, ABC):
    def __init__(self, ctx: SharedObject, message: str):
        super().__init__(ctx)
        self._menu_message = f"{message}"

    def _handlers(self) -> t.OrderedDict[str, MenuItem]:
        ord_dict = OrderedDict()
        add_menu_item(ord_dict, "Active (awaiting approvals)", "a", self._handle_relevant)
        add_menu_item(ord_dict, "History (executed or expired)", "h", self._handle_history)
        add_menu_item(ord_dict, "All", "l", self._handle_all)
        add_menu_item(ord_dict, "Back", 'b', self._handle_exit)

        return ord_dict

    @abstractmethod
    def _handle_relevant(self):
        raise NotImplementedError

    @abstractmethod
    def _handle_history(self):
        raise NotImplementedError

    @abstractmethod
    def _handle_all(self):
        raise NotImplementedError

#