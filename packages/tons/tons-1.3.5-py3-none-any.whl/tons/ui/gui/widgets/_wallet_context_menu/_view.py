import functools
from typing import Protocol, List

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QWidget

from ._model import WalletContextMenuModel, WalletMoveToLocationKind, WalletMoveToLocation
from tons.ui.gui.utils import get_elided_text, get_icon


class Presenter(Protocol):
    def on_wallet_selected(self): ...
    def on_transfer_from(self): ...
    def on_transfer_to(self): ...
    def on_init_wallet(self): ...
    def on_copy_selected_wallet_address(self): ...
    def on_export_wallet(self): ...
    def on_show_in_scanner(self): ...
    def on_move_to(self, location: WalletMoveToLocation): ...
    def on_delete_wallet(self): ...


class WalletContextMenuView(QMenu):
    _move_to = pyqtSignal(WalletMoveToLocation)

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.action_edit = QAction('Edit', self)
        self.action_transfer_from = QAction('Transfer from...', self)
        self.action_transfer_to = QAction('Transfer to...', self)
        self.action_init = QAction('Init wallet...', self)
        self.action_copy = QAction("Copy address", self)
        self.action_to_addr_and_pk = QAction("Export to .addr and .pk...")
        self.action_show_in_scanner = QAction("Show in scanner", self)
        self.action_delete = QAction("Delete")

        self.addAction(self.action_edit)
        self.addSeparator()
        for action in [self.action_transfer_from, self.action_transfer_to]:
            self.addAction(action)
        self.addSeparator()
        self._menu_move_to = self.addMenu("Move to")
        self._move_actions: List[QAction] = []
        self.addSeparator()
        self.addAction(self.action_copy)
        self.addAction(self.action_show_in_scanner)
        self.addSeparator()
        self.addAction(self.action_init)
        self.addSeparator()
        self.addAction(self.action_to_addr_and_pk)
        self.addSeparator()
        self.addAction(self.action_delete)

        self.setStyleSheet("""QMenu::item:disabled {
                                  color: grey;
                              }""")

    def setup_signals(self, presenter: Presenter):
        self.action_edit.triggered.connect(presenter.on_wallet_selected)
        self.action_transfer_from.triggered.connect(presenter.on_transfer_from)
        self.action_transfer_to.triggered.connect(presenter.on_transfer_to)
        self.action_init.triggered.connect(presenter.on_init_wallet)
        self.action_copy.triggered.connect(presenter.on_copy_selected_wallet_address)
        self.action_to_addr_and_pk.triggered.connect(presenter.on_export_wallet)
        self.action_show_in_scanner.triggered.connect(presenter.on_show_in_scanner)
        self.action_delete.triggered.connect(presenter.on_delete_wallet)

        self._move_to.connect(presenter.on_move_to)

    def display_model(self, model: WalletContextMenuModel):
        self.action_init.setEnabled(model.action_init_enabled)
        self.action_transfer_from.setEnabled(model.action_transfer_from_enabled)
        self.action_to_addr_and_pk.setEnabled(model.action_to_addr_and_pk_enabled)

        self._menu_move_to.clear()
        self._move_actions.clear()

        for location in model.move_to_locations:
            icon = {
                WalletMoveToLocationKind.keystore: get_icon('lock-solid.svg'),
                WalletMoveToLocationKind.local_whitelist: get_icon('contact-local.svg'),
                WalletMoveToLocationKind.global_whitelist: get_icon('contact-global.svg')
            }[location.kind]
            if location.kind == WalletMoveToLocationKind.global_whitelist:
                self._menu_move_to.addSeparator()

            shrinked_name = get_elided_text(location.name,
                                            self._menu_move_to.font(),
                                            model.max_allowed_width)

            move_action = self._menu_move_to.addAction(icon, shrinked_name)
            slot = functools.partial(self._emit_move_to, location)
            move_action.triggered.connect(slot)

            self._move_actions.append(move_action)

        if model.disabled_location_idx is not None:
            self._move_actions[model.disabled_location_idx].setEnabled(False)

    def _emit_move_to(self, location: WalletMoveToLocation):
        self._move_to.emit(location)
