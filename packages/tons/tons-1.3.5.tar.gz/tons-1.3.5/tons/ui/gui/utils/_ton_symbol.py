from PyQt6.QtWidgets import QWidget


class TonSymbolView:
    def __init__(self, ton_widget: QWidget):
        self._ton_widget = ton_widget

    def show(self):
        self._ton_widget.setVisible(True)

    def hide(self):
        self._ton_widget.setVisible(False)
