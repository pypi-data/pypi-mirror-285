from enum import Enum, auto
from typing import Dict, Protocol, Optional

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QPushButton, QAbstractButton

from tons.ui.gui.utils import slot_exc_handler


class KeystoreWindowSubcontext(Enum):
    wallets = auto()
    dns = auto()


class Observer(Protocol):
    def on_subcontext_switched(self): ...


class KeystoreWindowSubcontextViewComponent(QObject):
    _subcontext_changed = pyqtSignal()

    def __init__(self,
                 button_wallets: QPushButton, button_dns: QPushButton):
        super().__init__()
        self._buttons: Dict[KeystoreWindowSubcontext, QPushButton] = {
            KeystoreWindowSubcontext.wallets: button_wallets,
            KeystoreWindowSubcontext.dns: button_dns,
        }

        for kind, button in self._buttons.items():
            slot = self.on_clicked_slot_factory(kind)
            button.clicked.connect(slot)

        self.selected_subcontext = KeystoreWindowSubcontext.wallets
        self.on_clicked_slot_factory(self.selected_subcontext)()

        self._default_button_text: Dict[QAbstractButton, str] = {
            button: button.text()
            for button in self._buttons.values()
        }

    def setup_signals(self, observer: Observer):
        self._subcontext_changed.connect(observer.on_subcontext_switched)

    def on_clicked_slot_factory(self, subcontext: KeystoreWindowSubcontext):
        @slot_exc_handler()
        def slot(_=None):
            self.selected_subcontext = subcontext
            self._subcontext_changed.emit()
            self._buttons[subcontext].setChecked(True)
            for kind_, button in self._buttons.items():
                if kind_ == subcontext:
                    continue
                button.setChecked(False)

        return slot

    def click(self, subcontext: KeystoreWindowSubcontext):
        self.on_clicked_slot_factory(subcontext)()

    def get_button(self, subcontext: KeystoreWindowSubcontext) -> QPushButton:
        return self._buttons[subcontext]

    def set_subcontext_elements_count(self, subcontext: KeystoreWindowSubcontext, count: Optional[int]):
        button = self.get_button(subcontext)
        default_text = self._default_button_text[button]
        text = default_text
        if count is not None:
            text += f" ({count})"
        button.setText(text)
