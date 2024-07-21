from tons.tonclient.utils import BaseKeyStore
from tons.ui._utils import SharedObject
from ._model import CreateBatchWalletModel
from ._view import CreateBatchWalletView
from ._presenter import CreateBatchWalletPresenter
from .._base import NormalWindow


class CreateBatchWalletWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore):
        super().__init__()
        self._model = CreateBatchWalletModel(ctx.config, keystore, ctx.keystores)
        self._view = CreateBatchWalletView()
        self._presenter: CreateBatchWalletPresenter = CreateBatchWalletPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)


__all__ = ['CreateBatchWalletWindow']