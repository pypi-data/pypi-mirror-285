from typing import Optional

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from tons.tonclient.utils._exceptions import RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError
from ._create_batch_wallet_progress import CreateBatchWalletProgressWindow
from ._create_batch_wallet_progress._model import BadRange
from ._create_batch_wallet_progress._presenter import WalletBatchCreateStatus
from ._model import CreateBatchWalletModel
from ._utils import range_is_valid, get_wallet_name, CreateBatchWalletTaskModel
from ._view import CreateBatchWalletView
from ..mixins.keystore_selection import KeystoreSelectPresenter
from ..mixins.wallet_version_selection import WalletVersionSelectPresenter
from ..mixins.workchain_selection import WorkchainSelectPresenter
from ...utils import slot_exc_handler


class CreateBatchWalletPresenter(QObject, KeystoreSelectPresenter, WalletVersionSelectPresenter,
                                 WorkchainSelectPresenter):
    created = pyqtSignal(str)  # keystore_name: str

    def __init__(self, model: CreateBatchWalletModel, view: CreateBatchWalletView):
        super().__init__()
        self._model: CreateBatchWalletModel = model
        self._view: CreateBatchWalletView = view
        self._display_model()
        self._progress_bar_window = None
        view.setup_signals(self)

    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        if self._view.from_idx is None or self._view.to_idx is None:
            self._view.notify_bad_range()
            return

        task = CreateBatchWalletTaskModel(
            comment=self._view.comment,
            version=self._view.version,
            workchain=self._view.workchain,
            min_idx=self._view.from_idx,
            max_idx=self._view.to_idx,
            prefix=self._view.prefix,
            suffix=self._view.suffix,
        )
        self._progress_bar_window = CreateBatchWalletProgressWindow(self._model._keystore, task)
        self._progress_bar_window.move_to_center(of=self._view)
        self._progress_bar_window.connect_created(self._on_wallet_created)
        self._progress_bar_window.show()

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_keystore_changed(self, new_name: str):
        self._model.set_keystore(new_name)

    @pyqtSlot()
    @slot_exc_handler()
    def on_pattern_changed(self):
        self._explain_pattern()

    @pyqtSlot(WalletBatchCreateStatus)
    @slot_exc_handler
    def _on_wallet_created(self, status: WalletBatchCreateStatus):
        self._progress_bar_window.close()

        if not status.success:
            if isinstance(status.exception, BadRange):
                self._view.notify_bad_range()
            elif isinstance(status.exception, RecordWithAddressAlreadyExistsError):
                self._view.notify_address_already_exists(status.exception.name, status.exception.address)
            elif isinstance(status.exception, RecordWithNameAlreadyExistsError):
                self._view.notify_name_exists()
            else:
                raise status.exception
        else:
            self.created.emit(self._model.keystore_name)
            self._view.close()


    def _display_model(self):
        self._display_versions()
        self._display_workchains()
        self._display_keystores()

    def _explain_pattern(self):
        self._view.display_sample_count()

        min_idx = self._view.from_idx
        max_idx = self._view.to_idx

        if not range_is_valid(min_idx, max_idx):
            self._view.explanation = self._view.default_explanation
            return

        prefix = self._view.prefix
        suffix = self._view.suffix

        wallet_1 = get_wallet_name(min_idx, prefix, suffix, min_idx, max_idx)
        wallet_2 = get_wallet_name(min_idx + 1, prefix, suffix, min_idx, max_idx)

        txt = f'Results: {wallet_1}, {wallet_2}...'
        self._view.explanation = txt


__all__ = ['CreateBatchWalletPresenter']
