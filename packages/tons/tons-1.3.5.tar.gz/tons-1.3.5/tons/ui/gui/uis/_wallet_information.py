from typing import Dict, Sequence

from PyQt6.QtWidgets import QWidget, QFrame

from . import ui_patch
from ._qt_assets import wallet_information


@ui_patch
class WalletInformationUI(wallet_information.Ui_Form):
    def post_setup_ui(self, form: QWidget):
        self.blockMnemonicsRevealed.hide()
        self.pushButtonCopyAddressData.resizeEvent(None)
        self.pushButtonCopySharpAddressCode.resizeEvent(None)

    @property
    def icons_map(self) -> Dict[QWidget, str]:
        matrix = dict()
        matrix[self.labelTonIcon] = "ton_symbol.svg"

        matrix[self.pushButtonQR] = "qrcode-solid.svg"
        for widget in (self.pushButtonCopySharpAddressCode,
                       self.pushButtonCopyAddressData,
                       self.pushButtonCopyBounceableAddress,
                       self.pushButtonCopyNonBounceableAddress,
                       self.pushButtonCopyRawAddress,
                       self.pushButtonCopyMnemonics
                       ):
            matrix[widget] = "copy-regular.svg"

        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
