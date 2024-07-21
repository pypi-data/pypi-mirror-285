from tons.tonclient.utils import BaseKeyStore
from tons.ui._utils import SharedObject
from ._model import ImportWalletFromPrivateKeyModel
from ._view import ImportWalletFromPrivateKeyView
from ._presenter import ImportWalletFromPrivateKeyPresenter
from .._base import NormalWindow


class ImportWalletFromPrivateKeyWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore):
        super().__init__()
        self._model = ImportWalletFromPrivateKeyModel(ctx.config, keystore, ctx.keystores)
        self._view: ImportWalletFromPrivateKeyView = ImportWalletFromPrivateKeyView()
        self._presenter = ImportWalletFromPrivateKeyPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)


__all__ = ['ImportWalletFromPrivateKeyWindow']