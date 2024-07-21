from tons.tonclient.utils import BaseKeyStore
from tons.ui._utils import SharedObject
from ._model import ImportWalletFromMnemonicsModel
from ._view import ImportWalletFromMnemonicsView
from ._presenter import ImportWalletFromMnemonicsPresenter
from .._base import NormalWindow


class ImportWalletFromMnemonicsWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore):
        super().__init__()
        self._model = ImportWalletFromMnemonicsModel(ctx.config, keystore, ctx.keystores)
        self._view: ImportWalletFromMnemonicsView = ImportWalletFromMnemonicsView()
        self._presenter = ImportWalletFromMnemonicsPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)


__all__ = ['ImportWalletFromMnemonicsWindow']