from tons.tonclient.utils import BaseKeyStore
from tons.ui._utils import SharedObject
from ._model import CreateWalletModel
from ._view import CreateWalletView
from ._presenter import CreateWalletPresenter
from .._base import NormalWindow


class CreateWalletWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore):
        super().__init__()
        self._model: CreateWalletModel = CreateWalletModel(ctx.config, keystore, ctx.keystores)
        self._view: CreateWalletView = CreateWalletView()
        self._presenter = CreateWalletPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)


__all__ = ['CreateWalletWindow']