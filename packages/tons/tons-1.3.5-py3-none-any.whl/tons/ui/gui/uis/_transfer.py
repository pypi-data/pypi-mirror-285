from typing import Tuple, Dict, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QLineEdit, QHBoxLayout, QWidget, QFrame

from ._base import ui_patch
from ._qt_assets import transfer


@ui_patch
class TransferUI(transfer.Ui_Form):
    def post_setup_ui(self, form):
        self.widgetFrom.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.widgetFromLayout = QHBoxLayout(self.widgetFrom)
        self.widgetFromLayout.setContentsMargins(0, 0, 0, 0)
        self.widgetFromLayout.setSpacing(0)
        self.widgetFromLayout.setObjectName("widgetFromLayout")

        self.widgetTo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.widgetToLayout = QHBoxLayout(self.widgetTo)
        self.widgetToLayout.setContentsMargins(0, 0, 0, 0)
        self.widgetToLayout.setSpacing(0)
        self.widgetToLayout.setObjectName("widgetToLayout")

        self.labelErrorSelectWallets.hide()

    @property
    def widgets_to_fix_font_size(self) -> Tuple[QLineEdit, ...]:
        return self.lineEditAmount, self.labelErrorSelectWallets

    # @property
    # def icons_map(self) -> Dict[QWidget, str]:
    #     return {self.labelIconWallet: "ton_symbol.svg"}

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line,
