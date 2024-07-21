from typing import Optional
from typing import Protocol

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal

from tons.ui.gui.uis import CreateBatchWalletProgressUI
from tons.ui.gui.utils import qt_exc_handler
from tons.ui.gui.windows._base import NormalView


class Presenter(Protocol):
    def on_password_entered(self): ...


class CreateBatchWalletProgressView(NormalView):
    _closed = pyqtSignal()

    def __init__(self, total_number: int, keystore_name: str):
        super().__init__(CreateBatchWalletProgressUI)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._ui.progressBar.setRange(0, total_number)
        self._keystore_label.setText(keystore_name)
        self._progress_bar_label.setText("Initializing...")

    def connect_closed(self, slot):
        self._closed.connect(slot)
        self._button_box.rejected.connect(self.close)

    @qt_exc_handler
    def closeEvent(self, a0: Optional[QtGui.QCloseEvent]) -> None:
        self._closed.emit()

    def update_information(self, idx: int, wallet_name: str):
        self._progress_bar.setProperty("value", idx)
        self._progress_bar_label.setText(f"Creating wallet: {wallet_name}")

    @property
    def _progress_bar(self):
        return self._ui.progressBar

    @property
    def _progress_bar_label(self):
        return self._ui.label

    @property
    def _keystore_label(self):
        return self._ui.labelKeystoreName

    @property
    def _button_box(self) -> QtWidgets.QDialogButtonBox:
        return self._ui.buttonBox
