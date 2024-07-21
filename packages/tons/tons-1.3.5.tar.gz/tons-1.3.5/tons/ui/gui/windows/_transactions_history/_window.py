from uuid import UUID

from PyQt6.QtCore import pyqtSlot

from tons.ui._utils import SharedObject
from tons.ui.gui.utils import BackgroundTaskService, EditAndRetryInfo
from ._model import TransactionsHistoryModel
from ._presenter import TransactionsHistoryPresenter
from .._base import NormalWindow
from ._view import TransactionsHistoryView
from ...widgets import TransactionListItemData


class TransactionsHistoryWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, background_service: BackgroundTaskService):
        super().__init__()
        self._view: TransactionsHistoryView = TransactionsHistoryView()
        self._model: TransactionsHistoryModel = TransactionsHistoryModel(ctx, background_service)
        self._presenter = TransactionsHistoryPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_selected(self, slot: pyqtSlot(TransactionListItemData)):
        self._presenter.transaction_selected.connect(slot)

    def connect_edit_and_retry(self, slot: pyqtSlot(EditAndRetryInfo)):
        self._presenter.edit_and_retry.connect(slot)

    def connect_cancel(self, slot: pyqtSlot(UUID)):
        self._presenter.cancel.connect(slot)
