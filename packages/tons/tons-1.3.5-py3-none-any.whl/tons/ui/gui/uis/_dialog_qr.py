from PyQt6.QtWidgets import QWidget, QDialogButtonBox

from ._base import ui_patch
from ._qt_assets import dialog_qr


@ui_patch
class DialogQRUI(dialog_qr.Ui_QrCodeDialog):
    def post_setup_ui(self, form: QWidget):
        form.setFixedSize(form.size())
        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).setText('OK')
