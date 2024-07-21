import datetime
from copy import deepcopy
from decimal import Decimal
from enum import Enum, auto
from functools import lru_cache
from typing import Any, Optional

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from tons.tonclient._client._base import AddressState
from ._item_data import WalletListItemData, WalletListItemKind
from ...utils import nastr


class WalletListItemDataRole(Enum):
    application_data = Qt.ItemDataRole.UserRole + 1  # wallet data (without search highlight)
    display_data = Qt.ItemDataRole.UserRole + 2      # wallet data (with search highlight)
    visible = Qt.ItemDataRole.UserRole + 3           # visibility flag (bool)
    obscure = Qt.ItemDataRole.UserRole + 4           # obscurity flag (bool)


class WalletListItem(QStandardItem):
    def __init__(self, wallet_data: WalletListItemData):
        super().__init__()
        self.wallet_data = wallet_data
        self.wallet_display_data = deepcopy(wallet_data)
        self.visible = True

    @property
    def wallet_data(self) -> WalletListItemData:  # TODO check none
        return self.data(WalletListItemDataRole.application_data.value)

    @wallet_data.setter
    def wallet_data(self, wallet_data: WalletListItemData):
        self.setData(wallet_data, WalletListItemDataRole.application_data.value)

    @property
    def wallet_display_data(self) -> WalletListItemData:  # TODO check none
        return self.data(WalletListItemDataRole.display_data.value)

    @wallet_display_data.setter
    def wallet_display_data(self, wallet_display_data: WalletListItemData):
        self.setData(wallet_display_data, WalletListItemDataRole.display_data.value)

    @property
    def visible(self) -> bool:
        return self.data(WalletListItemDataRole.visible.value)

    @visible.setter
    def visible(self, visible: bool):
        self.setData(visible, WalletListItemDataRole.visible.value)

    @property
    def obscure(self) -> bool:
        return self.data(WalletListItemDataRole.obscure.value)

    @obscure.setter
    def obscure(self, obscure: bool):
        self.setData(obscure, WalletListItemDataRole.obscure.value)


class WalletListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._obscure = False # TODO remove (?)


@lru_cache(maxsize=None)
def _kind_less_than(left: WalletListItemKind, right: WalletListItemKind):
    matrix = {
        WalletListItemKind.record: 0,
        WalletListItemKind.local_contact: 1,
        WalletListItemKind.global_contact: 2
    }
    return matrix[left] < matrix[right]


@lru_cache(maxsize=512)
def _name_less_than(left: Optional[str], right: Optional[str]):
    return nastr(left).lower() < nastr(right).lower()  # case-insensitive


@lru_cache(maxsize=None)
def _state_less_than(left: Optional[AddressState], right: Optional[AddressState]):
    matrix = {
        AddressState.active: 0,
        AddressState.frozen: 1,
        AddressState.non_exist: 2,
        AddressState.uninit: 3,
        None: 4
    }
    return matrix[left] < matrix[right]


@lru_cache(maxsize=512)
def _comment_less_than(left: Optional[str], right: Optional[str]):
    # empty comments go to the end
    if bool(left) and (not bool(right)):
        return True
    elif not(left and right):
        return False

    return left.lower() < right.lower()


@lru_cache(maxsize=512)
def _balance_less_than(left: Optional[Decimal], right: Optional[Decimal]):
    left = left or 0
    right = right or 0
    return left > right  # sort descending


@lru_cache(maxsize=512)
def _last_activity_less_than(left: Optional[datetime.datetime], right: Optional[datetime.datetime]):
    # empty activities go to the end
    if bool(left) and (not bool(right)):
        return True
    elif not (left and right):
        return False

    return left.timestamp() > right.timestamp()  # sort descending


def _state(wallet_data: WalletListItemData) -> Optional[AddressState]:
    try:
        return wallet_data.address_info.state
    except AttributeError:
        return None


def _last_activity(wallet_data: WalletListItemData) -> Optional[datetime.datetime]:
    try:
        return wallet_data.address_info.last_activity_datetime
    except AttributeError:
        return None


def _balance(wallet_data: WalletListItemData) -> Optional[Decimal]:
    try:
        return wallet_data.address_info.balance
    except AttributeError:
        return None


class SortMode(Enum):
    name = auto()
    status = auto()
    comment = auto()
    balance = auto()
    last_activity = auto()


class WalletListProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model: WalletListModel):
        super().__init__()
        self.setSourceModel(source_model)
        self.sort_mode = SortMode.name

    @property
    def _source_model(self) -> WalletListModel:
        return self.sourceModel()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self._source_model.index(source_row, 0, source_parent)
        return index.data(WalletListItemDataRole.visible.value)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_data: WalletListItemData = left.data(WalletListItemDataRole.application_data.value)
        right_data: WalletListItemData = right.data(WalletListItemDataRole.application_data.value)

        if _kind_less_than(left_data.kind, right_data.kind):
            return True
        elif left_data.kind != right_data.kind:
            return False

        if self.sort_mode == SortMode.name:
            return _name_less_than(left_data.name, right_data.name)
        elif self.sort_mode == SortMode.status:
            return _state_less_than(_state(left_data), _state(right_data))
        elif self.sort_mode == SortMode.comment:
            return _comment_less_than(left_data.comment, right_data.comment)
        elif self.sort_mode == SortMode.balance:
            return _balance_less_than(_balance(left_data), _balance(right_data))
        elif self.sort_mode == SortMode.last_activity:
            return _last_activity_less_than(_last_activity(left_data), _last_activity(right_data))
        else:
            raise NotImplementedError
