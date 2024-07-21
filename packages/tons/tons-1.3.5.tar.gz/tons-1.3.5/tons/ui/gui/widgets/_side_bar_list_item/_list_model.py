from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel

from ._item_model import SideBarListItemModel


class SideBarListItemDataRole(Enum):
    application_data = Qt.ItemDataRole.UserRole + 1  # sidebar list item data
    obscure = Qt.ItemDataRole.UserRole + 2  # obscurity flag (bool)


class SideBarListItem(QStandardItem):
    def __init__(self, item_model: SideBarListItemModel):
        super().__init__()
        self.item_model = item_model

    @property
    def item_model(self) -> SideBarListItemModel:  # TODO check none
        return self.data(SideBarListItemDataRole.application_data.value)

    @item_model.setter
    def item_model(self, item_data: SideBarListItemModel):
        self.setData(item_data, SideBarListItemDataRole.application_data.value)

    @property
    def obscure(self) -> bool:
        return self.data(SideBarListItemDataRole.obscure.value)

    @obscure.setter
    def obscure(self, obscure: bool):
        self.setData(obscure, SideBarListItemDataRole.obscure.value)


class SideBarListModel(QStandardItemModel):
    pass