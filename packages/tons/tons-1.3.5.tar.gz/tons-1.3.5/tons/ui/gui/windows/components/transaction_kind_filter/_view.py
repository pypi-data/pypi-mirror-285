from enum import Enum, auto
from typing import Dict, Protocol, Sequence, List, Optional

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton, QAbstractButton

from tons.ui.gui.promoted_widgets import WalletFilterButton
from tons.ui.gui.utils import slot_exc_handler
from tons.ui.gui.widgets import TransactionListItemKind


class TransactionsKindFilter(Enum):
    all_items = auto()
    complete = auto()
    pending = auto()
    errors = auto()


def transaction_list_item_kinds(filter_kind: TransactionsKindFilter) -> List[TransactionListItemKind]:
    matrix = {
        TransactionsKindFilter.all_items:
            [TransactionListItemKind.complete, TransactionListItemKind.pending, TransactionListItemKind.planned, TransactionListItemKind.error],
        TransactionsKindFilter.complete:
            [TransactionListItemKind.complete],
        TransactionsKindFilter.pending:
            [TransactionListItemKind.pending, TransactionListItemKind.planned],
        TransactionsKindFilter.errors:
            [TransactionListItemKind.error]
    }
    return matrix[filter_kind]


class Observer(Protocol):
    def display_filter(self): ...


class TransactionsKindFilterSelectViewComponent(QObject):
    _kind_selected = pyqtSignal()

    def __init__(self,
                 button_all_items: QPushButton, button_complete_transactions: QPushButton,
                 button_pending_transactions: QPushButton, button_error_transactions: QPushButton):
        super().__init__()
        self._buttons: Dict[TransactionsKindFilter, QPushButton] = {
            TransactionsKindFilter.all_items: button_all_items,
            TransactionsKindFilter.complete: button_complete_transactions,
            TransactionsKindFilter.pending: button_pending_transactions,
            TransactionsKindFilter.errors: button_error_transactions
        }

        for kind, button in self._buttons.items():
            slot = self.on_clicked_slot_factory(kind)
            button.clicked.connect(slot)

        self._selected_filter = TransactionsKindFilter.all_items
        self.on_clicked_slot_factory(TransactionsKindFilter.all_items)()

        self._default_button_text: Dict[QAbstractButton, str] = {
            button: button.text()
            for button in self._buttons.values()
        }

    def setup_signals(self, presenter: Observer):
        self._kind_selected.connect(presenter.display_filter)

    def on_clicked_slot_factory(self, kind: TransactionsKindFilter):
        @slot_exc_handler()
        def slot(_=None):
            self._selected_filter = kind
            self._kind_selected.emit()
            self._buttons[kind].setChecked(True)
            for kind_, button in self._buttons.items():
                if kind_ == kind:
                    continue
                button.setChecked(False)

        return slot

    def match(self):
        pass

    def click(self, kind: TransactionsKindFilter):
        self.on_clicked_slot_factory(kind)()

    @property
    def selected_kinds(self) -> Sequence[TransactionListItemKind]:
        return transaction_list_item_kinds(self._selected_filter)

    def get_button(self, kind: TransactionsKindFilter) -> WalletFilterButton:
        return self._buttons[kind]

    def set_tx_kind_count(self, kind: TransactionsKindFilter, count: Optional[int]):
        button = self.get_button(kind)
        default_text = self._default_button_text[button]
        text = default_text
        button.setText(text)
        button.set_count(count)
