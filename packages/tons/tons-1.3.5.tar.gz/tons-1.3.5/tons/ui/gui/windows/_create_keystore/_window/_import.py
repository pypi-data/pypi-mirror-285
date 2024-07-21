from tons.tonclient.utils._keystores import KeystoreBackup
from tons.ui._utils import SharedObject
from .._model import ImportKeystoreModel
from .._presenter import ImportKeystorePresenter
from .._view import ImportKeystoreView
from ..._base import NormalWindow


class ImportKeystoreWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, keystore_backup: KeystoreBackup, backup_file_path: str):
        super().__init__()
        self._model: ImportKeystoreModel = ImportKeystoreModel(ctx.keystores, keystore_backup)  # todo pass ctx instead of keystores
        self._view: ImportKeystoreView = ImportKeystoreView(backup_file_path)
        self._presenter = ImportKeystorePresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)
