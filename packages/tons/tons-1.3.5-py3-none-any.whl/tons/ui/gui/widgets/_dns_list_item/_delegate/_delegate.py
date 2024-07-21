import contextlib
from typing import Optional

from PyQt6.QtCore import QModelIndex, QSize, QRect, Qt
from PyQt6.QtGui import QPainter, QCursor, QPalette
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QListView, QStyle

from ._paint import draw_dns_model_in_rectangle
from .._item_data import DnsListItemData
from .._list_model import DnsListItemDataRole
from ._rectangles import DnsItemRectangles
from ._sizes import selection_rectangle_radius


@contextlib.contextmanager
def _paint_context(painter: QPainter, item_view_rectangle: QRect):
    painter.save()
    painter.translate(item_view_rectangle.topLeft())
    painter.setClipRect(item_view_rectangle.translated(-item_view_rectangle.topLeft()))
    yield
    painter.restore()


def _draw_selection_rectangle(option: QStyleOptionViewItem, painter: QPainter, item_view_rectangle: QRect):
    # TODO refactor DRY
    selection_color = option.palette.color(QPalette.ColorRole.Highlight)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(selection_color)
    painter.drawRoundedRect(item_view_rectangle, selection_rectangle_radius(), selection_rectangle_radius())
    painter.restore()


def _need_draw_separator(index: QModelIndex, widget: QListView) -> bool:
    if index.row() == 0:
        return False
    try:
        return widget.selectedIndexes()[0].row() not in [index.row(), index.row() - 1]
    except (IndexError, AttributeError):
        pass
    return True


class DnsListItemDelegate(QStyledItemDelegate):
    """ The man himself """
    def paint(self, painter: Optional[QPainter], option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        options = QStyleOptionViewItem(option)

        self.initStyleOption(options, index)

        widget: QListView = option.widget
        style = widget.style()
        item_view_rectangle = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options, widget)

        selected_rows = [i.row() for i in widget.selectedIndexes()]
        if index.row() in selected_rows:
            _draw_selection_rectangle(option, painter, item_view_rectangle)

        dns_data: DnsListItemData = index.data(DnsListItemDataRole.display_data.value) or \
                                          index.data(DnsListItemDataRole.application_data.value)
        if dns_data is None:
            return

        filtered_by_this_wallet = bool(index.data(DnsListItemDataRole.filtered_by_wallet.value))
        obscure = bool(index.data(DnsListItemDataRole.obscure.value))
        skeleton = bool(index.data(DnsListItemDataRole.skeleton.value))

        draw_dns_model_in_rectangle(painter, item_view_rectangle, dns_data,
                                    option.widget.viewport().mapFromGlobal(QCursor().pos()),
                                    filtered_by_wallet=filtered_by_this_wallet,
                                    need_draw_separator=_need_draw_separator(index, widget),
                                    obscure=obscure,
                                    skeleton=skeleton)

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> QSize:
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(DnsItemRectangles.preferred_height())
        return size_hint


__all__ = ['DnsListItemDelegate']