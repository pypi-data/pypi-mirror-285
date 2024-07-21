from typing import Protocol

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from pydantic import BaseModel

from tons.tonclient.utils import BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError
from tons.tonsdk.contract.wallet import Wallets
from tons.ui.gui.exceptions import GuiException
from tons.ui.gui.windows._create_batch_wallet._utils import range_is_valid, get_wallet_name, CreateBatchWalletTaskModel
from tons.ui.gui.windows.mixins.keystore_selection import KeystoreSelectModel
from tons.ui.gui.windows.mixins.wallet_version_selection import WalletVersionSelectModel
from tons.ui.gui.windows.mixins.workchain_selection import WorkchainSelectModel


class WalletCreated(BaseModel):
    idx: int
    name: str


class Presenter(Protocol):
    @pyqtSlot(WalletCreated)
    def on_wallet_created(self): ...


class CreateBatchWalletProgressModel(QObject, KeystoreSelectModel, WalletVersionSelectModel, WorkchainSelectModel):
    _item_created = pyqtSignal(WalletCreated)

    def __init__(self,
                 task: CreateBatchWalletTaskModel,
                 keystore: BaseKeyStore):
        super().__init__()
        self._task = task
        self._keystore = keystore
        self.is_running = True

    def setup_on_wallet_created(self, presenter: Presenter):
        self._item_created.connect(presenter.on_wallet_created)

    def create_wallets(self):
        if not range_is_valid(self._task.min_idx, self._task.max_idx):
            raise BadRange(self._task.min_idx, self._task.max_idx)

        with self._keystore.restore_on_failure():
            for progress_idx, wallet_idx in enumerate(range(self._task.min_idx, self._task.max_idx + 1)):
                if not self.is_running:
                    raise StopIteration

                wallet_name = get_wallet_name(wallet_idx, self._task.prefix, self._task.suffix,
                                              self._task.min_idx, self._task.max_idx)
                mnemonics, _, _, _ = Wallets.create(self._task.version, self._task.workchain)
                self._keystore.add_new_record(wallet_name,
                                              mnemonics,
                                              self._task.version,
                                              self._task.workchain,
                                              comment=self._task.comment,
                                              save=False)
                self._item_created.emit(WalletCreated(idx=progress_idx, name=wallet_name))

            self._keystore.save()


class BadRange(GuiException):
    def __init__(self, min_idx: int, max_idx: int):
        self.min_idx = min_idx
        self.max_idx = max_idx
        desc = f'Bad range: from {min_idx} to {max_idx}'
        super().__init__(desc)


__all__ = ["CreateBatchWalletProgressModel", "RecordWithAddressAlreadyExistsError", "RecordWithNameAlreadyExistsError",
           "BadRange"]
