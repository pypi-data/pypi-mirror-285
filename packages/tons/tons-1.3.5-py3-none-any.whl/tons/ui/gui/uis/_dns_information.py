from typing import Dict, Sequence, List, Union

from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QLineEdit

from . import ui_patch
from ._qt_assets import dns_information


@ui_patch
class DnsInformationUI(dns_information.Ui_Form):
    def post_setup_ui(self, form: QWidget):
        self._clear_values()

    @property
    def icons_map(self) -> Dict[QWidget, str]:
        matrix = dict()

        for widget in (self.pushButtonCopyDomain,
                       self.pushButtonCopyContractAddress,
                       ):
            matrix[widget] = "copy-regular.svg"

        matrix[self.labelDNSIcon] = "dns_item.svg"
        matrix[self.labelWalletIcon] = "wallet-solid.svg"

        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,

    def _clear_values(self):
        texts_to_clear: List[Union[QLabel, QLineEdit]] = [
            self.labelDomainValue,
            self.labelExpiresValueDate,
            self.labelExpiresValueTime,
            self.labelExpiresInDays,
            self.labelWallet,
            self.labelAddressMask,
            self.labelOwnershipStatusValue,
            self.lineEditContractAddress
        ]
        for text in texts_to_clear:
            text.setText('')


__all__ = ['DnsInformationUI']
