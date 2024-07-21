from datetime import datetime
from typing import Optional, Protocol

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QColor

from tons.logging_ import setup_logging
from tons.ui.gui.utils import TextDisplayProperty, blended_hint_color, html_text_colored, setup_fonts, slot_exc_handler

from tons.ui.gui.promoted_widgets import DomainLabel, AddressMaskLabel, WalletInteractiveLabel, AddressLineEdit, \
    InDaysLabel
from tons.ui.gui.uis._dns_information import DnsInformationUI
from tons.ui.gui.windows._base import NormalFixedSizeView

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QDialogButtonBox, QAbstractButton, QWidget


class Presenter(Protocol):
    def on_wallet_label_clicked(self): ...


class DnsInformationView(NormalFixedSizeView):
    ownership_status = TextDisplayProperty('labelOwnershipStatusValue')
    contract_address = TextDisplayProperty('lineEditContractAddress')
    owner_wallet_name = TextDisplayProperty('labelWallet')
    expires_in = TextDisplayProperty('labelExpiresInDays')

    def __init__(self, *args, **kwargs):
        super().__init__(DnsInformationUI, *args, **kwargs)
        self._expires: Optional[datetime] = None
        self._setup_signals()
        self._advanced_block.hide()

    @property
    def _advanced_block(self) -> QWidget:
        return self._ui.advancedOptionsBlock

    @property
    def _advanced_button_block(self) -> QWidget:
        return self._ui.moreOptionsButtonBlock

    @property
    def _advanced_button(self) -> QAbstractButton:
        return self._ui.toolButtonShowAdvancedOptions

    @property
    def _label_domain(self) -> DomainLabel:
        return self._ui.labelDomainValue

    @property
    def _label_wallet_address(self) -> AddressMaskLabel:
        return self._ui.labelAddressMask

    @property
    def _label_wallet(self) -> WalletInteractiveLabel:
        return self._ui.labelWallet

    @property
    def _label_ownership_status(self) -> QLabel:
        return self._ui.labelOwnershipStatusValue

    @property
    def _line_edit_contract_address(self) -> AddressLineEdit:
        return self._ui.lineEditContractAddress

    @property
    def _label_expires_date(self) -> QLabel:
        return self._ui.labelExpiresValueDate

    @property
    def _label_expires_time(self) -> QLabel:
        return self._ui.labelExpiresValueTime

    @property
    def _label_expires_in_days(self) -> InDaysLabel:
        return self._ui.labelExpiresInDays

    @property
    def _dialog_button_box(self) -> QDialogButtonBox:
        return self._ui.buttonBox

    @property
    def _cancel_button(self) -> QAbstractButton:
        return self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_show_advanced_options(self):
        self._advanced_button_block.hide()
        self._advanced_block.show()

    @property
    def domain(self) -> Optional[str]:
        return self._label_domain.domain

    @domain.setter
    def domain(self, value: str):
        self._label_domain.domain = value

    @property
    def owner_wallet_address(self) -> Optional[str]:
        return self._label_wallet_address.address

    @owner_wallet_address.setter
    def owner_wallet_address(self, value: str):
        self._label_wallet_address.address = value

    @property
    def expires(self) -> Optional[datetime]:
        return self._expires

    @expires.setter
    def expires(self, value: datetime):
        self._expires = value
        self.__set_expires()

    def __set_expires(self):
        # if self._expires is None:
        #     self._label_expires_date.setText('')
        #     self._label_expires_time.setText('')

        date = self._expires.strftime("%Y %B %d")
        formatted_seconds = html_text_colored("%S", self._expires_seconds_color)
        time = self._expires.strftime('%H:%M:' + formatted_seconds)
        self._label_expires_date.setText(date)
        self._label_expires_time.setText(time)

    @property
    def _expires_seconds_color(self) -> QColor:
        return blended_hint_color()

    def _setup_signals(self):
        self._cancel_button.clicked.connect(self.close)
        self._advanced_button.clicked.connect(self._on_show_advanced_options)

    def setup_signals(self, presenter: Presenter):
        self._label_wallet.clicked.connect(presenter.on_wallet_label_clicked)


def main():
    from tons.utils.packaging.gui import convert_qt_ui
    convert_qt_ui()
    app = QApplication(sys.argv)
    setup_logging('qt')
    setup_fonts()
    view = DnsInformationView()

    view.domain = 'tonfactory'
    view.contract_address = 'EQDnGtUF7vtfCGZ2Hw0buHjfcINyKnD0XLtdreolytg0JuWN'
    view.ownership_status = 'Owned'
    view.owner_wallet_name = 'My flashy wallet'
    view.owner_wallet_address = 'EQDnGtUF7vtfCGZ2Hw0buHjfcINyKnD0XLtdreolytg0JuWN'
    view.expires = datetime(2024, 9, 11, 8, 46, 0, 0)
    view.show()
    app.exec()


if __name__ == "__main__":
    main()


__all__ = ['DnsInformationView']
