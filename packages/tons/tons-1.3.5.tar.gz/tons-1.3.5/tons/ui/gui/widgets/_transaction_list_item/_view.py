import datetime
from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPaintEvent, QPainter, QCursor, QPalette
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout

from tons.logging_ import setup_logging
from ._delegate import draw_transaction_model_in_rectangle
from tons.ui.gui.widgets._transaction_list_item._colors import TransactionColors
from tons.ui.gui.widgets._transaction_list_item._fonts import TransactionFonts
from ._delegate import TransactionRectangles
from ._item_data import TransactionListItemData, TransactionListItemKind
from .._base import AbstractListItemView
from ...utils import qt_exc_handler, UpdateOnMouseMovementFilter, html_text_font, html_text_colored

_DRAW_DEBUG = False


class TransactionListItemView(AbstractListItemView):
    """ for testing purposes only """
    def __init__(self, *, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._model: Optional[TransactionListItemData] = None
        self.setMinimumHeight(TransactionRectangles.preferred_height())
        self.setMouseTracking(True)
        self._mouse_filter = UpdateOnMouseMovementFilter(self)

    def display_model(self, model: TransactionListItemData):
        self._model = model

    @qt_exc_handler
    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        if self._model is None:
            return
        draw_transaction_model_in_rectangle(QPainter(self), self.geometry(), self._model,
                                    self.mapFromGlobal(QCursor().pos()),
                                    draw_debug=_DRAW_DEBUG)

    def sizeHint(self) -> QSize:
        sz = super().sizeHint()
        sz.setHeight(TransactionRectangles.preferred_height())
        return sz


def _transaction_view_test():
    setup_logging('qt')
    app = QApplication([])

    widget = QWidget()
    widget.setWindowTitle('DnsListItemView demo')
    layout = QVBoxLayout(widget)
    view = TransactionListItemView(parent=widget)
    layout.addWidget(view)

    sum = html_text_font("10.239482", family=TransactionFonts().mono.family())
    sum = html_text_colored(sum, TransactionColors().highlight)

    data = TransactionListItemData(
        kind=TransactionListItemKind.pending,
        description=f'Transfer {sum} to Bill Gates',
        error='Floating point number error: the amount is too small',
        time_start=datetime.datetime.now(),
        time_finish=None
    )

    layout.setContentsMargins(0,0,0,0)

    view.display_model(data)
    geo = widget.geometry()
    geo.setHeight(view.sizeHint().height())
    geo.setWidth(1000)

    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, palette.color(QPalette.ColorRole.Base))
    widget.setPalette(palette)

    widget.setGeometry(geo)
    widget.show()

    app.exec()


__all__ = ['TransactionListItemView', '_transaction_view_test']
