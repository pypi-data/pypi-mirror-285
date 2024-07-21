from typing import Optional

from PyQt6.QtCore import QRect, Qt, QModelIndex, QSize
from PyQt6.QtGui import QPainter, QPalette
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QListView, QStyle

from ._distances import SideBarListItemDistances as _Distances
from .._item_model import SideBarListItemModel as _ItemModel
from .._list_model import SideBarListItemDataRole as _DataRole
from ._paint import draw_sidebar_model_in_rectangle as _draw_model_in_rectangle
from ._rectangles import SideBarListItemRectangles as _Rectangles


def _draw_selection_rectangle(option: QStyleOptionViewItem, painter: QPainter, item_view_rectangle: QRect):
    # TODO refactor DRY
    selection_color = option.palette.color(QPalette.ColorRole.Highlight)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(selection_color)
    painter.drawRoundedRect(item_view_rectangle,
                            _Distances().selection_rectangle_radius,
                            _Distances().selection_rectangle_radius)
    painter.restore()


def _get_item_model(index: QModelIndex) -> Optional[_ItemModel]:
    return index.data(_DataRole.application_data.value)


def _adjust_to_scrollbar(item_view_rect: QRect, widget: QListView):
    if widget.verticalScrollBar().isVisible():
        scroll_bar_width = widget.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
        item_view_rect.setRight(item_view_rect.right() - scroll_bar_width)


class SideBarListItemDelegate(QStyledItemDelegate):
    """ The man himself """
    # TODO refactor DRY delegates
    def paint(self, painter: Optional[QPainter], option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        options = QStyleOptionViewItem(option)

        self.initStyleOption(options, index)

        widget: QListView = option.widget
        style = widget.style()
        item_view_rectangle = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options, widget)

        selected = index.row() in (i.row() for i in widget.selectedIndexes())
        if selected:
            _draw_selection_rectangle(option, painter, item_view_rectangle)

        item_model: _ItemModel = _get_item_model(index)
        if item_model is None:
            return

        obscure = bool(index.data(_DataRole.obscure.value))

        _adjust_to_scrollbar(item_view_rectangle, widget)

        _draw_model_in_rectangle(painter,
                                 item_view_rectangle,
                                 item_model,
                                 selected,
                                 obscure)

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> QSize:
        size_hint = super().sizeHint(option, index)
        item_model = _get_item_model(index)
        if item_model is None:
            preferred_height = 0
        else:
            preferred_height = _Rectangles.preferred_height(item_model)

        size_hint.setHeight(preferred_height)
        return size_hint


__all__ = ['SideBarListItemDelegate']