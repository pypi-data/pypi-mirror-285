from typing import Protocol, Iterable, Optional

from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal
from pydantic import BaseModel

from tons.ui.gui.utils import slot_exc_handler
from tons.ui.gui.windows._create_batch_wallet._create_batch_wallet_progress._model import WalletCreated


class Model(Protocol):
    def create_wallets(self) -> Iterable: ...

    def setup_item_processed(self, presenter): ...

    def setup_on_wallet_created(self, presenter): ...


class View(Protocol):
    def setup_signals(self, presenter): ...

    def update_information(self, idx: int, wallet_name: str): ...

    def connect_closed(self, slot): ...


class WalletBatchCreateStatus(BaseModel):
    exception: Optional[Exception]

    @property
    def success(self):
        return self.exception is None

    class Config:
        arbitrary_types_allowed = True


class CreateBatchWalletProgressPresenter(QObject):
    created = pyqtSignal(WalletBatchCreateStatus)

    def __init__(self, model: Model, view: View):
        super().__init__()
        self._model = model
        self._model.setup_on_wallet_created(self)
        self._view = view

    def create_wallets(self):
        try:
            self._model.create_wallets()
        except StopIteration:
            pass
        except Exception as e:
            self.created.emit(WalletBatchCreateStatus(exception=e))
        else:
            self.created.emit(WalletBatchCreateStatus(exception=None))

    @pyqtSlot(WalletCreated)
    @slot_exc_handler
    def on_wallet_created(self, wallet_created: WalletCreated):
        self._view.update_information(wallet_created.idx, wallet_created.name)
