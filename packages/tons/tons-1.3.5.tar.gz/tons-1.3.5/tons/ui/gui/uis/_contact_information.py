from typing import Dict, Sequence

from PyQt6.QtWidgets import QWidget, QFrame

from . import ui_patch
from ._qt_assets import contact_information


@ui_patch
class ContactInformationUI(contact_information.Ui_Form):
    @property
    def icons_map(self) -> Dict[QWidget, str]:
        matrix = dict()
        matrix[self.labelTonIcon] = "ton_symbol.svg"

        matrix[self.pushButtonQR] = "qrcode-solid.svg"
        for widget in (self.pushButtonCopySharpAddressCode,
                       self.pushButtonCopyAddressData,
                       self.pushButtonCopyAddress,
                       self.pushButtonCopyAddressType2,
                       self.pushButtonCopyAddressType3
                       ):
            matrix[widget] = "copy-regular.svg"

        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,