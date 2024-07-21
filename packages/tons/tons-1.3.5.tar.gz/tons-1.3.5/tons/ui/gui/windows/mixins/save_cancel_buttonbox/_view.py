from typing import Protocol

from PyQt6.QtWidgets import QDialogButtonBox, QPushButton, QWidget


class UI(Protocol):
    buttonBox: QDialogButtonBox


class SaveCancelButtonBoxView:
    _ui: UI

    def init_button_box(self, widget: QWidget):
        self._cancel_button.clicked.connect(widget.close)

    @property
    def _button_box(self) -> QDialogButtonBox:
        return self._ui.buttonBox

    @property
    def _save_button(self) -> QPushButton:
        return self._button_box.button(QDialogButtonBox.StandardButton.Save)

    @property
    def _cancel_button(self) -> QPushButton:
        return self._button_box.button(QDialogButtonBox.StandardButton.Cancel)
