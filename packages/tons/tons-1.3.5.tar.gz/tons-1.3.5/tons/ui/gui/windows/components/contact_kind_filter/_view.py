from enum import Enum, auto
from typing import Dict, Protocol, Sequence, List, Optional

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton, QAbstractButton

from tons.ui.gui.utils import slot_exc_handler
from tons.ui.gui.widgets import WalletListItemKind


class ContactKindFilter(Enum):
    all_items = auto()
    keystore_wallets = auto()
    local_whitelist = auto()
    global_whitelist = auto()


def wallet_list_item_kinds(filter_kind: ContactKindFilter) -> List[WalletListItemKind]:
    matrix = {
        ContactKindFilter.all_items:
            [WalletListItemKind.record, WalletListItemKind.local_contact, WalletListItemKind.global_contact],
        ContactKindFilter.keystore_wallets:
            [WalletListItemKind.record],
        ContactKindFilter.local_whitelist:
            [WalletListItemKind.local_contact],
        ContactKindFilter.global_whitelist:
            [WalletListItemKind.global_contact]
    }
    return matrix[filter_kind]


class Observer(Protocol):
    def on_kind_selected(self): ...


class ContactKindFilterSelectViewComponent(QObject):
    _kind_selected = pyqtSignal()

    def __init__(self,
                 button_all_items: QPushButton, button_keystore_wallets: QPushButton,
                 button_local_whitelist: QPushButton, button_global_whitelist: QPushButton):
        super().__init__()
        self._buttons: Dict[ContactKindFilter, QPushButton] = {
            ContactKindFilter.all_items: button_all_items,
            ContactKindFilter.keystore_wallets: button_keystore_wallets,
            ContactKindFilter.local_whitelist: button_local_whitelist,
            ContactKindFilter.global_whitelist: button_global_whitelist
        }

        for kind, button in self._buttons.items():
            slot = self.on_clicked_slot_factory(kind)
            button.clicked.connect(slot)

        self._selected_filter = ContactKindFilter.all_items
        self.on_clicked_slot_factory(ContactKindFilter.all_items)()

        self._default_button_text: Dict[QAbstractButton, str] = {
            button: button.text()
            for button in self._buttons.values()
        }

    def setup_signals(self, presenter: Observer):
        self._kind_selected.connect(presenter.on_kind_selected)

    def on_clicked_slot_factory(self, kind: ContactKindFilter):
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

    def click(self, kind: ContactKindFilter):
        self.on_clicked_slot_factory(kind)()

    @property
    def selected_kinds(self) -> Sequence[WalletListItemKind]:
        return wallet_list_item_kinds(self._selected_filter)

    def get_button(self, kind: ContactKindFilter) -> QPushButton:
        return self._buttons[kind]

    def set_wallet_kind_count(self, kind: ContactKindFilter, count: Optional[int]):
        button = self.get_button(kind)
        default_text = self._default_button_text[button]
        text = default_text
        if count is not None:
            text += f" ({count})"
        button.setText(text)
