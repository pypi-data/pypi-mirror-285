from typing import Protocol, Dict, Optional, Iterator, Sequence

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QModelIndex, QPoint
from PyQt6.QtGui import QCursor, QGuiApplication
from PyQt6.QtWidgets import QPushButton, QWidget, QListView

from tons.ui.gui.uis import TransactionsHistoryUI
from tons.ui.gui.utils import TextDisplayProperty, slot_exc_handler, EditAndRetryInfo
from tons.ui.gui.widgets import TransactionListItemData, TransactionListItemKind, TransactionListItemDataRole, \
    TransactionListItem, TransactionListModel, TransactionListProxyModel, TransactionListItemDelegate, \
    TransactionRectangles, TransactionButton
from .._base import NormalView
from ..components.transaction_kind_filter import TransactionsKindFilterSelectViewComponent, TransactionsKindFilter, \
    transaction_list_item_kinds


class Presenter(Protocol):
    def on_transaction_list_item_selected(self, transaction_list_item_model: TransactionListItemData): ...
    def on_show_tx_in_scanner(self, transaction_list_item_model: TransactionListItemData): ...
    def on_edit_and_retry(self, transaction_list_item_model: TransactionListItemData): ...
    def on_cancel(self, transaction_list_item_model: TransactionListItemData): ...
    def on_tx_right_pressed(self, transaction_item_data: TransactionListItemData): ...


class TransactionsHistoryView(NormalView):
    _create_new_contact = pyqtSignal()
    _transaction_selected = pyqtSignal(TransactionListItemData)
    _edit_and_retry = pyqtSignal(TransactionListItemData)
    _show_in_scanner = pyqtSignal(TransactionListItemData)
    _cancel = pyqtSignal(TransactionListItemData)
    _transaction_right_press = pyqtSignal(TransactionListItemData)

    keystore_name = TextDisplayProperty('labelKeystoreName')
    transaction_count = TextDisplayProperty('labelWalletCount')

    def __init__(self):
        super().__init__(TransactionsHistoryUI)
        self._list_model_transactions = TransactionListModel()
        self._list_proxy_model_transactions = TransactionListProxyModel(self._list_model_transactions)
        self._list_transaction_delegate = TransactionListItemDelegate()
        self._list_transaction_delegate.setup_animation_updates(self._list_view_transactions)
        self._list_proxy_model_transactions.setDynamicSortFilter(False)  # very important

        self._list_view_transactions.setMouseTracking(True)
        self._list_view_transactions.setModel(self._list_proxy_model_transactions)
        self._list_view_transactions.setItemDelegate(self._list_transaction_delegate)
        self._list_view_transactions.setUniformItemSizes(True)

        self._transaction_statistics: Dict[TransactionListItemKind, int] = dict()
        self._clear_transaction_statistics()

        self._transaction_kind_filter = TransactionsKindFilterSelectViewComponent(
            self._button_all_items, self._button_complete_transactions,
            self._button_pending_transactions, self._button_errors_transactions)
        self._setup_signals()
        self.display_all_items_count = False

    def _setup_signals(self):
        self._list_view_transactions.doubleClicked.connect(self._on_list_view_transactions_double_clicked)
        self._list_view_transactions.clicked.connect(self._on_list_view_transactions_clicked)
        self._list_view_transactions.pressed.connect(self._on_list_view_transactions_pressed)
        self._transaction_kind_filter.setup_signals(self)
        self._button_cancel_all.clicked.connect(self._on_button_cancel_all_clicked)

    def setup_signals(self, presenter: Presenter):
        self._transaction_selected.connect(presenter.on_transaction_list_item_selected)
        self._show_in_scanner.connect(presenter.on_show_tx_in_scanner)
        self._edit_and_retry.connect(presenter.on_edit_and_retry)
        self._cancel.connect(presenter.on_cancel)
        self._transaction_right_press.connect(presenter.on_tx_right_pressed)

    def set_transaction_items(self, transaction_list: Sequence[TransactionListItemData]):
        self._clear_transactions()
        for tx_data in transaction_list:
            list_item = TransactionListItem(tx_data)
            self._list_model_transactions.appendRow(list_item)

        self.display_filter()
        self._update_statistics()
        self.display_transaction_kind_count()
        self._update_cancel_all_button_visibility()

    def _update_cancel_all_button_visibility(self):
        self._widget_cancel_all.setVisible(self._any_cancellable_transactions_exist())

    def _any_cancellable_transactions_exist(self) -> bool:
        return any(item.tx_data.cancellable for item in self._transactions_list_items())

    @pyqtSlot()
    @slot_exc_handler()
    def display_filter(self):
        for item in self._transactions_list_items():
            self._display_transaction_item_filter(item)
        self._invalidate_transactions_filter()

    def display_transaction_kind_count(self):
        for tx_kind in TransactionsKindFilter:
            if tx_kind == TransactionsKindFilter.all_items and not self.display_all_items_count:
                self._transaction_kind_filter.set_tx_kind_count(tx_kind, None)
                continue
            count = 0
            for kind in transaction_list_item_kinds(tx_kind):
                count += self.get_displayed_item_count_by_kind(kind)

            self._transaction_kind_filter.set_tx_kind_count(tx_kind, count)

    def get_displayed_item_count_by_kind(self, kind: TransactionListItemKind) -> int:
        return self._transaction_statistics[kind]

    def _update_statistics(self):
        self._clear_transaction_statistics()
        for item in self._transactions_list_items():
            self._transaction_statistics[item.tx_data.kind] += 1

    def _clear_transactions(self):
        self._list_model_transactions.clear()

    def _invalidate_transactions_filter(self):
        self._list_proxy_model_transactions.invalidateFilter()

    def _transactions_list_items(self) -> Iterator[TransactionListItem]:
        for row in range(self._list_model_transactions.rowCount()):
            yield self._list_model_transactions.item(row)

    def _display_transaction_item_filter(self, item: TransactionListItem):
        item.visible = item.tx_data.kind in self._transaction_kind_filter.selected_kinds

    def _clear_transaction_statistics(self):
        for kind in TransactionListItemKind:
            self._transaction_statistics[kind] = 0

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_list_view_transactions_double_clicked(self, model_index: QModelIndex):
        tx_data = model_index.data(TransactionListItemDataRole.application_data.value)
        self._on_transaction_selected(tx_data)

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_list_view_transactions_clicked(self, model_index: QModelIndex):
        local_mouse_position = self._list_view_transactions.viewport().mapFromGlobal(QCursor().pos())
        tx_data = model_index.data(TransactionListItemDataRole.application_data.value)
        rectangles = TransactionRectangles(tx_data, self._list_view_transactions.visualRect(model_index))
        if local_mouse_position in rectangles.button_hover:
            self._emit_list_view_transactions_clicked_signal(tx_data)

    def _emit_list_view_transactions_clicked_signal(self, tx_data: TransactionListItemData):
        if tx_data.button_to_display is None:
            return
        if tx_data.button_to_display == TransactionButton.view_in_scanner:
            self._show_in_scanner.emit(tx_data)
        if tx_data.button_to_display == TransactionButton.edit_and_retry:
            self._edit_and_retry.emit(tx_data)
        if tx_data.button_to_display == TransactionButton.cancel:
            self._cancel.emit(tx_data)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_create_new_contact(self):
        self._create_new_contact.emit()

    @pyqtSlot(QModelIndex)
    @slot_exc_handler()
    def _on_list_view_transactions_pressed(self, index: QModelIndex):
        if QGuiApplication.mouseButtons() == Qt.MouseButton.RightButton:
            data = index.data(TransactionListItemDataRole.application_data.value)
            self._transaction_right_press.emit(data)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_button_cancel_all_clicked(self):
        for item in self._transactions_list_items():
            if item.tx_data.cancellable:
                self._cancel.emit(item.tx_data)

    def _on_transaction_selected(self, transaction_data: Optional[TransactionListItemData]):
        pass
        # if transaction_data is None:
        #     self._show_message_box_select_transaction()
        #     return
        # self.close()
        # self._transaction_selected.emit(transaction_data)

    @property
    def _button_all_items(self) -> QPushButton:
        return self._ui.pushButtonAllItems

    @property
    def _button_complete_transactions(self) -> QPushButton:
        return self._ui.pushButtonCompleteTransactions

    @property
    def _button_pending_transactions(self) -> QPushButton:
        return self._ui.pushButtonPendingTransactions

    @property
    def _button_errors_transactions(self) -> QPushButton:
        return self._ui.pushButtonErrorsTransactions

    @property
    def _button_cancel_all(self) -> QPushButton:
        return self._ui.pushButtonCancelAll

    @property
    def _widget_cancel_all(self) -> QWidget:
        return self._ui.widgetCancelAll

    @property
    def _list_view_transactions(self) -> QListView:
        return self._ui.listViewTransactions

    @property
    def _widget_filter_buttons(self) -> QWidget:
        return self._ui.widgetFilterButtons

    @property
    def mouse_position(self) -> QPoint:
        return QCursor().pos()
