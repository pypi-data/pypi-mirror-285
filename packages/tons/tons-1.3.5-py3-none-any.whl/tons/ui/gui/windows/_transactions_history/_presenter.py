import itertools
import uuid
from typing import Sequence, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from tons.tonclient._client._base import TransactionCanceled
from tons.ui.gui.utils import QABCMeta, slot_exc_handler, BackgroundTaskService, show_transaction_in_scanner, \
    EditAndRetryInfo
from tons.ui.gui.widgets import TransactionListItemData
from tons.ui.gui.widgets._tx_context_menu._model import TransactionContextMenuModel
from tons.ui.gui.widgets._tx_context_menu._view import TransactionContextMenuView
from ._model import TransactionsHistoryModel
from ._view import TransactionsHistoryView


class TransactionsHistoryPresenter(QObject, metaclass=QABCMeta):
    transaction_selected = pyqtSignal(TransactionListItemData)
    edit_and_retry = pyqtSignal(EditAndRetryInfo)
    cancel = pyqtSignal(uuid.UUID)

    def __init__(self, model: TransactionsHistoryModel, view: TransactionsHistoryView):
        super().__init__()
        self._view: TransactionsHistoryView = view
        self._view.setup_signals(self)
        self._model: TransactionsHistoryModel = model
        self._model.setup_signals(self)

        self._show_transactions()

        self._tx_context_menu = TransactionContextMenuView(parent=self._view)
        self._tx_context_menu_model: Optional[TransactionContextMenuModel] = None
        self._tx_context_menu.setup_signals(self)

    def _show_transactions(self):
        transactions: List[TransactionListItemData] = []

        for task_id, tx in self._model.pending_tasks():
            if self._model.task_is_cancelled(task_id):
                continue
            transactions += TransactionListItemData.from_background_transaction(tx,
                                                                                self._model.task_is_taken(task_id),
                                                                                task_id)

        for task_id, tx in self._model.finished_tasks():
            if self._model.task_is_cancelled(task_id):
                """ failsafe, if something goes wrong 
                    and a cancelled transaction still gets sent - 
                    show it in the transactions list """
                if tx.result.is_cancelled():
                    continue
            transactions += TransactionListItemData.from_background_transaction(tx,
                                                                                self._model.task_is_taken(task_id),
                                                                                task_id)

        self._view.set_transaction_items(transactions)

    @pyqtSlot()
    @slot_exc_handler()
    def on_transactions_queue_changed(self):
        self._show_transactions()

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_tx_info_fetched(self, tx_hash):
        self._show_transactions()

    @pyqtSlot(TransactionListItemData)
    @slot_exc_handler()
    def on_transaction_list_item_selected(self, transaction_list_item_model: TransactionListItemData):
        self.transaction_selected.emit(transaction_list_item_model)

    @pyqtSlot(TransactionListItemData)
    @slot_exc_handler()
    def on_show_tx_in_scanner(self, transaction_list_item_model: TransactionListItemData):
        self._show_tx_in_scanner(transaction_list_item_model)

    def _show_tx_in_scanner(self, transaction_list_item_model: TransactionListItemData):
        show_transaction_in_scanner(transaction_list_item_model.tx_hash,
                                    self._model.network_is_testnet(),
                                    self._model.scanner(),
                                    transaction_list_item_model.tx_info)

    @pyqtSlot(TransactionListItemData)
    @slot_exc_handler()
    def on_edit_and_retry(self, transaction_list_item_model: TransactionListItemData):
        self._edit_and_retry(transaction_list_item_model)

    def _edit_and_retry(self, transaction_list_item_model):
        if transaction_list_item_model.edit_and_retry_info:
            self.edit_and_retry.emit(transaction_list_item_model.edit_and_retry_info)

    @pyqtSlot(TransactionListItemData)
    @slot_exc_handler()
    def on_cancel(self, transaction_list_item_model: TransactionListItemData):
        self._cancel(transaction_list_item_model)

    def _cancel(self, transaction_list_item_model):
        if transaction_list_item_model.task_id is not None:
            self.cancel.emit(transaction_list_item_model.task_id)

    @pyqtSlot(TransactionListItemData)
    @slot_exc_handler()
    def on_tx_right_pressed(self, transaction_item_data: TransactionListItemData):
        self._tx_context_menu_model = TransactionContextMenuModel.from_transaction_list_item_data(transaction_item_data)
        self._tx_context_menu.display_model(self._tx_context_menu_model)
        self._tx_context_menu.exec(self._view.mouse_position)

    @pyqtSlot()
    @slot_exc_handler()
    def on_cancel_selected_transaction(self):
        self._cancel(self._tx_context_menu_model.item_data)

    @pyqtSlot()
    @slot_exc_handler()
    def on_edit_and_retry_selected_transaction(self):
        self._edit_and_retry(self._tx_context_menu_model.item_data)

    @pyqtSlot()
    @slot_exc_handler()
    def on_check_in_scanner_selected_transaction(self):
        self._show_tx_in_scanner(self._tx_context_menu_model.item_data)
