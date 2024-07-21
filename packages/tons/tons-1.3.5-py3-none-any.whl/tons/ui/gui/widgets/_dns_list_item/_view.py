from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPaintEvent, QPainter, QPalette, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication

from tons.logging_ import setup_logging
from tons.tonclient._client._base import NftItemInfoResult, NftItemType
from ._delegate import draw_dns_model_in_rectangle, DnsItemRectangles
from ._item_data import DnsListItemData
from .._base import AbstractListItemView
from ...utils import slot_exc_handler, UpdateOnMouseMovementFilter, qt_exc_handler

_DRAW_DEBUG = True


class DnsListItemView(AbstractListItemView):
    """ Used for testing purposes only """
    def __init__(self, *, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._model: Optional[DnsListItemData] = None
        self.setMinimumHeight(DnsItemRectangles.preferred_height())
        self.setMouseTracking(True)
        self._mouse_filter = UpdateOnMouseMovementFilter(self)

    def display_model(self, model: DnsListItemData):
        self._model = model

    @qt_exc_handler
    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        if self._model is None:
            return
        draw_dns_model_in_rectangle(QPainter(self), self.geometry(), self._model,
                                    self.mapFromGlobal(QCursor().pos()),
                                    draw_debug=_DRAW_DEBUG)

    def sizeHint(self) -> QSize:
        sz = super().sizeHint()
        sz.setHeight(DnsItemRectangles.preferred_height())
        return sz


def _dns_view_test():
    setup_logging('qt')
    app = QApplication([])

    widget = QWidget()
    widget.setWindowTitle('DnsListItemView demo')
    layout = QVBoxLayout(widget)
    view = DnsListItemView(parent=widget)
    layout.addWidget(view)

    data = DnsListItemData.from_nft_info_result(wallet_name="My wallet",
                                                wallet_address="UQC5IfWFQ73EkjeBqno4wMnnJPoh-6MYN9sE_aX8H6OaEh5E",
                                                nft_info=NftItemInfoResult(
                                                    nft_item_type=NftItemType.dns_item,
                                                    owner_address="UQC5IfWFQ73EkjeBqno4wMnnJPoh-6MYN9sE_aX8H6OaEh5E",
                                                    dns_domain='tonfactory',
                                                    dns_last_fill_up_time=1701082716,

                                                ),
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


__all__ = ['DnsListItemView', '_dns_view_test']
