from typing import Protocol

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QWidget

from tons.ui.gui.widgets._refresh_dns_menu import RefreshDnsMenuModel


class Presenter(Protocol):
    def on_action_dns_refresh_all(self): ...
    def on_action_dns_refresh_expiring_in(self): ...


class RefreshDnsMenuView(QMenu):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.action_refresh_all = QAction('All domains')
        self.action_refresh_expiring_in = QAction('Expiring in ... months')

        for action in [self.action_refresh_all, self.action_refresh_expiring_in]:
            self.addAction(action)

    def display_model(self, model: RefreshDnsMenuModel):
        self.action_refresh_expiring_in.setText(f'Expiring in {model.max_expiring_in} months')

    def setup_signals(self, presenter: Presenter):
        self.action_refresh_all.triggered.connect(presenter.on_action_dns_refresh_all)
        self.action_refresh_expiring_in.triggered.connect(presenter.on_action_dns_refresh_expiring_in)
