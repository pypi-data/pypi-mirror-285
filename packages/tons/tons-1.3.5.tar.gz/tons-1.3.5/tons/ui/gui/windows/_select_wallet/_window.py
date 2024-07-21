from typing import Type

from PyQt6.QtCore import pyqtSlot

from tons.ui._utils import SharedObject
from ._model import SelectWalletModel
from ._presenter import SelectWalletDestinationPresenter
from ._presenter import SelectWalletPresenter
from ._presenter import SelectWalletSourcePresenter
from .._base import NormalWindow
from ._view import SelectWalletView
from ...utils import LocalWhitelistLocation
from ...widgets import WalletListItemData


class SelectWalletWindow(NormalWindow):
    Presenter: Type[SelectWalletPresenter]

    def __init__(self, ctx: SharedObject, keystore_name: str):
        super().__init__()
        self._model = SelectWalletModel(ctx, keystore_name)
        self._view = SelectWalletView()
        self._presenter = self.Presenter(self._model, self._view)

        self.init_normal_window()

    def connect_selected(self, slot: pyqtSlot(WalletListItemData)):
        self._presenter.wallet_selected.connect(slot)

    def connect_contact_created(self, slot: pyqtSlot(LocalWhitelistLocation)):
        self._presenter.contact_created.connect(slot)


class SelectWalletDestinationWindow(SelectWalletWindow):
    Presenter = SelectWalletDestinationPresenter


class SelectWalletSourceWindow(SelectWalletWindow):
    Presenter = SelectWalletSourcePresenter
