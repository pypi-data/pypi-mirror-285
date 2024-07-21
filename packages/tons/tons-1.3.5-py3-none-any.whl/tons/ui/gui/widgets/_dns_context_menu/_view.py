from typing import Protocol

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QWidget

from ._model import DnsContextMenuModel


class Presenter(Protocol):
    def on_copy_domain(self): ...
    def on_show_dns_in_scanner(self): ...
    def on_copy_dns_contract_address(self): ...
    def on_show_dns_contract_in_scanner(self): ...
    def on_copy_owner_or_max_bidder_address(self): ...
    def on_dns_refresh_selected_list_item(self): ...
    def on_dns_selected(self): ...


class DnsContextMenuView(QMenu):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)
        self.action_show_info = QAction('Details')
        self.action_copy_domain = QAction('Copy domain')
        self.action_show_dns_in_scanner = QAction('Show on dns.ton.org')
        self.action_copy_dns_contract_address = QAction('Copy contract address')
        self.action_show_dns_contract_in_scanner = QAction('Show contract in scanner')
        self.action_copy_owner_or_max_bidder_address = QAction('Copy owner / max bidder address')
        self.action_refresh = QAction('Refresh ownership')

        self._add_actions()
        self._set_stylesheet()

    def setup_signals(self, presenter: Presenter):
        self.action_show_info.triggered.connect(presenter.on_dns_selected)
        self.action_copy_domain.triggered.connect(presenter.on_copy_domain)
        self.action_show_dns_in_scanner.triggered.connect(presenter.on_show_dns_in_scanner)
        self.action_copy_dns_contract_address.triggered.connect(presenter.on_copy_dns_contract_address)
        self.action_show_dns_contract_in_scanner.triggered.connect(presenter.on_show_dns_contract_in_scanner)
        self.action_copy_owner_or_max_bidder_address.triggered.connect(presenter.on_copy_owner_or_max_bidder_address)
        self.action_refresh.triggered.connect(presenter.on_dns_refresh_selected_list_item)

    def _add_actions(self):
        self.addAction(self.action_show_info)
        self.addSeparator()
        self.addAction(self.action_copy_domain)
        self.addAction(self.action_show_dns_in_scanner)
        self.addSeparator()
        self.addAction(self.action_copy_dns_contract_address)
        self.addAction(self.action_show_dns_contract_in_scanner)
        self.addSeparator()
        self.addAction(self.action_copy_owner_or_max_bidder_address)
        self.addSeparator()
        self.addAction(self.action_refresh)

    def _set_stylesheet(self):
        self.setStyleSheet("""QMenu::item:disabled {
                                          color: grey;
                                      }""")

    def display_model(self, model: DnsContextMenuModel):
        if model.owned is None:
            self.action_copy_owner_or_max_bidder_address.setText('Copy owner / max bidder address')
        elif model.owned is True:
            self.action_copy_owner_or_max_bidder_address.setText('Copy owner address')
        elif model.owned is False:
            self.action_copy_owner_or_max_bidder_address.setText('Copy max bidder address')
            self.action_refresh.setText('Claim ownership')
