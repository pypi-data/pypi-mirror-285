from enum import Enum, auto
from typing import Dict, Protocol, Sequence, List, Optional

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton, QAbstractButton

from tons.ui.gui.utils import slot_exc_handler
from tons.ui.gui.widgets import DnsListItemKind, DnsListItemData


class DnsKindFilter(Enum):
    all_items = auto()
    owned = auto()
    taken = auto()
    by_wallet = auto()


def dns_list_item_kinds(filter_kind: DnsKindFilter) -> List[DnsListItemKind]:
    matrix = {
        DnsKindFilter.all_items:
            [DnsListItemKind.owned, DnsListItemKind.taken,],
        DnsKindFilter.owned:
            [DnsListItemKind.owned],
        DnsKindFilter.taken:
            [DnsListItemKind.taken],
        DnsKindFilter.by_wallet:
            [],
    }
    return matrix[filter_kind]


class Observer(Protocol):
    def on_dns_kind_selected(self): ...


class DnsKindFilterSelectViewComponent(QObject):
    _dns_kind_selected = pyqtSignal()

    def __init__(self,
                 button_all_items: QPushButton, button_owned: QPushButton,
                 button_taken: QPushButton, button_by_wallet: QPushButton):
        super().__init__()
        button_by_wallet.hide()
        self._buttons: Dict[DnsKindFilter, QPushButton] = {
            DnsKindFilter.all_items: button_all_items,
            DnsKindFilter.owned: button_owned,
            DnsKindFilter.taken: button_taken,
            DnsKindFilter.by_wallet: button_by_wallet,
        }

        for kind, button in self._buttons.items():
            slot = self.on_clicked_slot_factory(kind)
            button.clicked.connect(slot)

        self._selected_filter = DnsKindFilter.all_items
        self._selected_wallet_name = None
        self.on_clicked_slot_factory(DnsKindFilter.all_items)()

        self._default_button_text: Dict[DnsKindFilter, str] = {
            kind: button.text()
            for kind, button in self._buttons.items()
        }

    def setup_signals(self, presenter: Observer):
        self._dns_kind_selected.connect(presenter.on_dns_kind_selected)

    def get_button_text(self, kind: DnsKindFilter):
        if kind == DnsKindFilter.by_wallet:
            return self._selected_wallet_name
        else:
            return self._default_button_text[kind]

    def on_clicked_slot_factory(self, kind: DnsKindFilter):
        @slot_exc_handler()
        def slot(_=None):
            self._selected_filter = kind
            self._dns_kind_selected.emit()
            self._buttons[kind].setChecked(True)
            for kind_, button in self._buttons.items():
                if kind_ == kind:
                    continue
                button.setChecked(False)
        return slot

    def click(self, kind: DnsKindFilter):
        self.on_clicked_slot_factory(kind)()

    @property
    def selected_kinds(self) -> Sequence[DnsListItemKind]:
        return dns_list_item_kinds(self._selected_filter)

    def get_button(self, kind: DnsKindFilter) -> QPushButton:
        return self._buttons[kind]

    def set_dns_kind_count(self, kind: DnsKindFilter, count: Optional[int]):
        if kind == DnsKindFilter.by_wallet:
            return

        button = self.get_button(kind)
        text = self.get_button_text(kind)
        if count is not None and text is not None:
            text += f" ({count})"
        button.setText(text)

    def set_selected_wallet(self, wallet_name: Optional[str]):
        self._selected_wallet_name = wallet_name
        if wallet_name is not None:
            self._buttons[DnsKindFilter.by_wallet].setText(wallet_name)
            self._buttons[DnsKindFilter.by_wallet].click()

    @property
    def filtered_by_wallet(self):
        return self._selected_wallet_name is not None and self._selected_filter == DnsKindFilter.by_wallet

    def match(self, dns_data: DnsListItemData) -> bool:
        if self._selected_filter != DnsKindFilter.by_wallet:
            return dns_data.kind in self.selected_kinds
        elif self._selected_wallet_name is not None:
            return dns_data.wallet_name == self._selected_wallet_name
        else:
            return False
