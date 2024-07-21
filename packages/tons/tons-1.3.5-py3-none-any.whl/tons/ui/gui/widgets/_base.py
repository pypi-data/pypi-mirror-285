from abc import abstractmethod
from functools import lru_cache
from typing import Optional

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget, QApplication
from pydantic import BaseModel

from tons.ui.gui.utils import QABCMeta, theme_is_dark


class AbstractListItemModel(BaseModel):
    pass


class AbstractListItemView(QWidget, metaclass=QABCMeta):
    @abstractmethod
    def display_model(self, model: AbstractListItemModel):
        raise NotImplementedError


# def get_list_item_model(list_widget_item: QListWidgetItem):
#     list_item_model = list_widget_item.data(Qt.ItemDataRole.UserRole)
#     assert isinstance(list_item_model, AbstractListItemModel)
#     return list_item_model


# def set_list_item_model(list_widget_item: QListWidgetItem, list_item_model: AbstractListItemModel):
#     list_widget_item.setData(Qt.ItemDataRole.UserRole, list_item_model)


# def list_widget_items(list_widget: QListWidget) -> Iterator[Tuple[QListWidgetItem, AbstractListItemModel, QWidget]]:
#     for idx in range(list_widget.count()):
#         item = list_widget.item(idx)
#         data = get_list_item_model(item)
#         widget = list_widget.itemWidget(item)
#         yield item, data, widget


# def add_item_widget(list_widget: QListWidget, model: AbstractListItemModel, view_cls: Type[AbstractListItemView]) -> \
#         Tuple[QListWidgetItem, AbstractListItemView]:
#     """ Adds a widget to the QListWidget, with the corresponding model """
#     item_widget = view_cls(parent=list_widget)
#     item_widget.display_model(model)
#     layout = item_widget.layout()
#     layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
#
#     list_widget_item = QListWidgetItem()
#     list_widget_item.setSizeHint(item_widget.sizeHint())
#     set_list_item_model(list_widget_item, model)
#
#     list_widget.addItem(list_widget_item)
#     list_widget.setItemWidget(list_widget_item, item_widget)
#
#     return list_widget_item, item_widget


# def get_list_item_model_from_index(list_widget: QListWidget, index: QModelIndex) -> AbstractListItemModel:
#     list_widget_item = list_widget.itemFromIndex(index)
#     list_item_model = get_list_item_model(list_widget_item)
#     return list_item_model


@lru_cache
def obscure_rectangle_color(palette: Optional[QPalette] = None) -> QColor:
    gray_delta = 0x10
    if theme_is_dark():
        gray_delta = -gray_delta

    palette = palette or QApplication.palette()
    base_color = palette.base().color()
    return QColor(base_color.red() - gray_delta,
                  base_color.green() - gray_delta,
                  base_color.blue() - gray_delta,
                  0x80)


__all__ = ['AbstractListItemModel', 'AbstractListItemView', 'obscure_rectangle_color']
