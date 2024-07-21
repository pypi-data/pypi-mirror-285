from PyQt6.QtCore import QThread, pyqtSlot

from tons.tonclient.utils import BaseKeyStore
from ._model import CreateBatchWalletTaskModel, CreateBatchWalletProgressModel
from ._presenter import CreateBatchWalletProgressPresenter
from ._view import CreateBatchWalletProgressView
from ..._base import NormalWindow


class CreateBatchWalletProgressWindow(NormalWindow):
    def __init__(self, keystore: BaseKeyStore, task: CreateBatchWalletTaskModel):
        super().__init__()
        self._model = CreateBatchWalletProgressModel(task, keystore)
        self._view: CreateBatchWalletProgressView = CreateBatchWalletProgressView(task.max_idx - task.min_idx,
                                                                                  keystore.name)
        self._view.connect_closed(self._on_closed)
        self._presenter = CreateBatchWalletProgressPresenter(self._model, self._view)
        self.init_normal_window()
        self._thread = QThread()

    def show(self):
        super().show()
        self._thread.setObjectName('create wallets batch')
        self._presenter.moveToThread(self._thread)
        self._thread.started.connect(self._presenter.create_wallets)
        self._thread.start()

    @pyqtSlot()
    def _on_closed(self):
        self._model.is_running = False
        self._thread.quit()
        self._thread.wait()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)


__all__ = ['CreateBatchWalletProgressWindow']
