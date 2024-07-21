from abc import abstractmethod
from typing import Union, Type, Optional

from PyQt6 import QtGui
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QEvent, QSize
from PyQt6.QtGui import QScreen, QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget, QDialog, QLayout
from pydantic import BaseModel

from tons.tonclient.utils import BaseKeyStore, Record
from ..utils import move_to_center, QABCMeta
from ..widgets import WalletListItemData


class NormalView(QWidget):

    def __init__(self, ui_cls: Type):
        super().__init__()
        self._ui: ui_cls = ui_cls()
        self._ui.setupUi(self)


class NormalFixedSizeView(NormalView):
    """View that should not be resizable by the user, but its size can be adjusted by hiding/showing its sub-elements.

    Guidelines:
    This approach assumes that the window layout always automatically adjusts to the minimal possible value.
    Therefore, make the window freely resizable in Qt Designer (minsize=0,0 maxsize=inf,inf).
    Restrict its size by setting the minimal size of individual elements.
    ( for instance, in the "new keystore" window, the minimal width can be restricted by the minimum
    size of the "Name" horizontal block. )
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._disable_maximize_button()

    def _disable_maximize_button(self):
        """
        Reference:
        https://doc.qt.io/qt-5/qtwidgets-widgets-windowflags-example.html
        """
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)


class DialogView(QDialog):
    def __init__(self, ui_cls: Type):
        super().__init__()
        self._ui: ui_cls = ui_cls()
        self._ui.setupUi(self)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


class Window(QObject):
    _view: QWidget

    def move_to_center(self, of: Union[QScreen, QWidget]):
        move_to_center(self._view, of)


class NormalWindow(Window):
    _view: NormalView
    _closed = pyqtSignal(object)

    def init_normal_window(self):
        self.close_active_shorcut = QShortcut(QKeySequence("Ctrl+W"), self._view)
        self.close_active_shorcut.activated.connect(self._close_active_window)

    def _close_active_window(self):
        self.close()

    def show(self):
        self._view.show()
        self._view.setFocus()

    def close(self):
        self._view.close()

    @pyqtSlot()
    def on_closed(self):
        self._closed.emit(self)

    def connect_closed(self, slot):
        self._closed.connect(slot)


class DialogWindow(Window):
    def exec(self):
        self._view.exec()


class DeleteWalletSensitiveWindow(Window, metaclass=QABCMeta):
    @abstractmethod
    def notify_wallet_deleted(self, deleted_wallet: WalletListItemData, keystore_name: Optional[str]):
        raise NotImplementedError


class ShowWalletInformationIntent(BaseModel):
    keystore: BaseKeyStore
    record: Record

    class Config:
        arbitrary_types_allowed = True
