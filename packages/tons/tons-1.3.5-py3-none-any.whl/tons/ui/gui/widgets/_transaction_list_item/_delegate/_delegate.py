import contextlib
from typing import Optional

from PyQt6.QtCore import QModelIndex, QSize, QRect, Qt, QTimeLine
from PyQt6.QtGui import QPainter, QCursor, QPalette
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QListView, QStyle

from tons.ui.gui.utils import qt_exc_handler
from ._paint import draw_transaction_model_in_rectangle
from .._item_data import TransactionListItemData
from .._list_model import TransactionListItemDataRole
from ._rectangles import TransactionRectangles
from ._sizes import selection_rectangle_radius


@contextlib.contextmanager
def _paint_context(painter: QPainter, item_view_rectangle: QRect):
    painter.save()
    painter.translate(item_view_rectangle.topLeft())
    painter.setClipRect(item_view_rectangle.translated(-item_view_rectangle.topLeft()))
    yield
    painter.restore()


def _draw_selection_rectangle(option: QStyleOptionViewItem, painter: QPainter, item_view_rectangle: QRect):
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


class TransactionListItemDelegate(QStyledItemDelegate):
    """ The man himself """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self._timeline = self._setup_timeline()

    def _setup_timeline(self) -> QTimeLine:
        timeline = QTimeLine(1000, parent=self)
        timeline.setFrameRange(0, 20)
        timeline.setLoopCount(0)
        timeline.start()
        return timeline

    def setup_animation_updates(self, list_view: QListView):
        self._timeline.frameChanged.connect(list_view.viewport().update)

    @qt_exc_handler
    def paint(self, painter: Optional[QPainter], option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        options = QStyleOptionViewItem(option)

        self.initStyleOption(options, index)

        widget: QListView = option.widget
        style = widget.style()
        item_view_rectangle = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options, widget)

        selected_rows = [i.row() for i in widget.selectedIndexes()]
        if index.row() in selected_rows:
            _draw_selection_rectangle(option, painter, item_view_rectangle)

        transaction_data: TransactionListItemData = index.data(TransactionListItemDataRole.display_data.value) or \
                                            index.data(TransactionListItemDataRole.application_data.value)
        if transaction_data is None:
            return

        draw_transaction_model_in_rectangle(painter, item_view_rectangle, transaction_data,
                                            option.widget.viewport().mapFromGlobal(QCursor().pos()),
                                            need_draw_separator=_need_draw_separator(index, widget),
                                            frame_id=self._timeline.currentFrame(),
                                            max_frame_id=self._timeline.endFrame())

    @qt_exc_handler
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> QSize:
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(TransactionRectangles.preferred_height())
        return size_hint


__all__ = ['TransactionListItemDelegate']
