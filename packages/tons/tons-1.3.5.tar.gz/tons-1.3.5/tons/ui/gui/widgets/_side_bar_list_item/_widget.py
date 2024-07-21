from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPaintEvent, QPainter, QPalette
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication

from tons.logging_ import setup_logging
from ._delegate import draw_sidebar_model_in_rectangle as _draw_model, SideBarListItemRectangles as _Rectangles
from ._item_model import SideBarListItemModel as _Model, SideBarListItemKind
from .._base import AbstractListItemView
from ...utils import UpdateOnMouseMovementFilter, qt_exc_handler

_DRAW_DEBUG = True


class SideBarListItemView(AbstractListItemView):
    """ For testing purposes only """
    def __init__(self, *, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._model: Optional[_Model] = None

        self.setMouseTracking(True)
        self._mouse_filter = UpdateOnMouseMovementFilter(self)
        self._selected = False
        self._obscure = False

    def display_model(self, model: _Model):
        self._model = model
        self.setMinimumHeight(_Rectangles.preferred_height(model))

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        self._selected = value
        self.repaint()

    @qt_exc_handler
    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        if self._model is None:
            return
        _draw_model(QPainter(self), self.geometry(), self._model, self._selected, self._obscure,
                    draw_debug=_DRAW_DEBUG)

    @qt_exc_handler
    def sizeHint(self) -> QSize:
        sz = super().sizeHint()
        sz.setHeight(_Rectangles.preferred_height(self._model))
        return sz

    def set_obscure(self, obscure: bool):
        # TODO refactor property
        self._obscure = obscure


def _sidebar_view_test():
    setup_logging('qt')
    app = QApplication([])

    widget = QWidget()
    widget.setWindowTitle('SideBarListItemView demo')
    layout = QVBoxLayout(widget)
    view = SideBarListItemView(parent=widget)
    layout.addWidget(view)

    data = _Model(kind=SideBarListItemKind.global_whitelist,
                  name='My keystore',
                  balance=123.67,
                  count=21)

    layout.setContentsMargins(0,0,0,0)

    view.display_model(data)
    # view.selected = True
    # view.set_obscure(True)
    geo = widget.geometry()
    geo.setHeight(view.sizeHint().height())
    geo.setWidth(200)

    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, palette.color(QPalette.ColorRole.Base))
    widget.setPalette(palette)

    widget.setGeometry(geo)
    widget.show()

    app.exec()


__all__ = ['SideBarListItemView', '_sidebar_view_test']
