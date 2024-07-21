from PyQt6.QtWidgets import QDialogButtonBox

from tons.ui.gui.utils import qt_exc_handler


class MyDialogButtonBox(QDialogButtonBox):
    @qt_exc_handler
    def setStandardButtons(self, buttons: 'QDialogButtonBox.StandardButton') -> None:
        super().setStandardButtons(buttons)
        self._adjust_button_widths()

    def _adjust_button_widths(self):
        max_width = max(button.sizeHint().width() for button in self.buttons())
        for button in self.buttons():
            button.setMinimumWidth(max_width)


class SaveCancelDialogButtonBox(MyDialogButtonBox):
    save_button_title = ...

    @qt_exc_handler
    def setStandardButtons(self, buttons: 'QDialogButtonBox.StandardButton') -> None:
        assert buttons == QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        super().setStandardButtons(buttons)
        self.button(QDialogButtonBox.StandardButton.Save).setText(self.save_button_title)
        self._adjust_button_widths()


class CreateCancelDialogButtonBox(SaveCancelDialogButtonBox):
    save_button_title = 'Create'


class TransferCancelDialogButtonBox(SaveCancelDialogButtonBox):
    save_button_title = 'Transfer'


class SelectCancelDialogButtonBox(SaveCancelDialogButtonBox):
    save_button_title = 'Select'
