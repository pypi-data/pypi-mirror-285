import datetime
from copy import deepcopy
from enum import Enum, auto
from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from ._item_data import DnsListItemData
from ...utils import nastr


class DnsListItemDataRole(Enum):
    application_data = Qt.ItemDataRole.UserRole + 1  # dns data (without search highlight)
    display_data = Qt.ItemDataRole.UserRole + 2  # dns data (with search highlight)
    visible = Qt.ItemDataRole.UserRole + 3  # visibility flag (bool)
    obscure = Qt.ItemDataRole.UserRole + 4  # obscurity flag (bool)
    filtered_by_wallet = Qt.ItemDataRole.UserRole + 5  # is filtered by wallet flag (bool)
    skeleton = Qt.ItemDataRole.UserRole + 6  # is skeleton flag (bool)


class DnsListItem(QStandardItem):
    def __init__(self, dns_data: DnsListItemData, filtered_by_wallet: bool, skeleton: bool):
        super().__init__()
        self.dns_data = dns_data
        self.dns_display_data = deepcopy(dns_data)
        self.visible = True
        self.filtered_by_wallet = filtered_by_wallet
        self.skeleton = skeleton

    @property
    def dns_data(self) -> DnsListItemData:  # TODO check none
        return self.data(DnsListItemDataRole.application_data.value)

    @dns_data.setter
    def dns_data(self, dns_data: DnsListItemData):
        self.setData(dns_data, DnsListItemDataRole.application_data.value)

    @property
    def dns_display_data(self) -> DnsListItemData:  # TODO check none
        return self.data(DnsListItemDataRole.display_data.value)

    @dns_display_data.setter
    def dns_display_data(self, dns_display_data: DnsListItemData):
        self.setData(dns_display_data, DnsListItemDataRole.display_data.value)

    @property
    def visible(self) -> bool:
        return self.data(DnsListItemDataRole.visible.value)

    @visible.setter
    def visible(self, visible: bool):
        self.setData(visible, DnsListItemDataRole.visible.value)

    @property
    def filtered_by_wallet(self) -> bool:
        return self.data(DnsListItemDataRole.filtered_by_wallet.value)

    @filtered_by_wallet.setter
    def filtered_by_wallet(self, filtered_by_wallet: bool):
        self.setData(filtered_by_wallet, DnsListItemDataRole.filtered_by_wallet.value)

    @property
    def skeleton(self) -> bool:
        return self.data(DnsListItemDataRole.skeleton.value)

    @skeleton.setter
    def skeleton(self, skeleton: bool):
        self.setData(skeleton, DnsListItemDataRole.skeleton.value)

    @property
    def obscure(self) -> bool:
        return self.data(DnsListItemDataRole.obscure.value)

    @obscure.setter
    def obscure(self, obscure: bool):
        self.setData(obscure, DnsListItemDataRole.obscure.value)


class DnsListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._obscure = False   # TODO remove (?)


@lru_cache(maxsize=512)
def _name_less_than(left: Optional[str], right: Optional[str]):
    return nastr(left).lower() < nastr(right).lower()  # case-insensitive


@lru_cache(maxsize=512)
def _remaining_less_than(left: Optional[int], right: Optional[int]):
    if bool(left) and (not bool(right)):
        return True
    elif not (left and right):
        return False

    return left < right  # sort ascending


class DnsSortMode(Enum):
    remaining = auto()
    domain = auto()
    wallet = auto()


class DnsListProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model: DnsListModel):
        super().__init__()
        self.setSourceModel(source_model)
        self.dns_sort_mode = DnsSortMode.remaining

    @property
    def _source_model(self) -> DnsListModel:
        return self.sourceModel()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self._source_model.index(source_row, 0, source_parent)
        return index.data(DnsListItemDataRole.visible.value)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_data: DnsListItemData = left.data(DnsListItemDataRole.application_data.value)
        right_data: DnsListItemData = right.data(DnsListItemDataRole.application_data.value)

        if self.dns_sort_mode == DnsSortMode.remaining:
            return _remaining_less_than(left_data.dns_last_fill_up_time,
                                        right_data.dns_last_fill_up_time)
        elif self.dns_sort_mode == DnsSortMode.domain:
            return _name_less_than(left_data.domain, right_data.domain)
        elif self.dns_sort_mode == DnsSortMode.wallet:
            return _name_less_than(left_data.wallet_name, right_data.wallet_name)
        else:
            raise NotImplementedError
