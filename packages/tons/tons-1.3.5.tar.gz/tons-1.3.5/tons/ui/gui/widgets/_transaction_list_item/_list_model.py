from copy import deepcopy
from enum import Enum

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from ._item_data import TransactionListItemData


class TransactionListItemDataRole(Enum):
    application_data = Qt.ItemDataRole.UserRole + 1  # wallet data (without search highlight)
    display_data = Qt.ItemDataRole.UserRole + 2  # wallet data (with search highlight)
    visible = Qt.ItemDataRole.UserRole + 3  # visibility flag (bool)
    obscure = Qt.ItemDataRole.UserRole + 4  # obscurity flag (bool)


class TransactionListItem(QStandardItem):
    def __init__(self, tx_data: TransactionListItemData):
        super().__init__()
        self.tx_data = tx_data
        self.visible = True

    @property
    def tx_data(self) -> TransactionListItemData:
        return self.data(TransactionListItemDataRole.application_data.value)

    @tx_data.setter
    def tx_data(self, tx_data: TransactionListItemData):
        self.setData(tx_data, TransactionListItemDataRole.application_data.value)

    @property
    def tx_display_data(self) -> TransactionListItemData:  # TODO check none
        return self.data(TransactionListItemDataRole.display_data.value)

    @tx_display_data.setter
    def tx_display_data(self, wallet_display_data: TransactionListItemData):
        self.setData(wallet_display_data, TransactionListItemDataRole.display_data.value)

    @property
    def visible(self) -> bool:
        return self.data(TransactionListItemDataRole.visible.value)

    @visible.setter
    def visible(self, visible: bool):
        self.setData(visible, TransactionListItemDataRole.visible.value)

    @property
    def obscure(self) -> bool:
        return self.data(TransactionListItemDataRole.obscure.value)

    @obscure.setter
    def obscure(self, obscure: bool):
        self.setData(obscure, TransactionListItemDataRole.obscure.value)


class TransactionListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._obscure = False


class TransactionListProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model: TransactionListModel):
        super().__init__()
        self.setSourceModel(source_model)

    @property
    def _source_model(self) -> TransactionListModel:
        return self.sourceModel()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self._source_model.index(source_row, 0, source_parent)
        return index.data(TransactionListItemDataRole.visible.value)
