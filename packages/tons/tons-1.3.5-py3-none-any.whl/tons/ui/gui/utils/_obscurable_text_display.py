from PyQt6.QtWidgets import QWidget

from tons.ui.gui.utils import set_widget_obscure, gibberish


class ObscurableTextDisplay:
    def __init__(self, widget: QWidget, obscure_length: bool = False):
        self._widget = widget
        try:
            self._actual_text = self._displayed_text
        except AttributeError:
            raise AttributeError(f'{type(self).__name__} not set correctly: no text() method found')
        self._obscure: bool = False
        self._obscure_length = obscure_length

    def get(self) -> str:
        return self._actual_text

    def set(self, value: str):
        self._actual_text = value
        self._update_display()

    def set_obscure(self, obscure: bool):
        self._obscure = obscure
        self._update_display()

    @property
    def obscure(self) -> bool:
        return self._obscure

    def _update_display(self):
        set_widget_obscure(self._widget, self._obscure)
        self._displayed_text = gibberish() if (self._obscure and self._obscure_length) else self._actual_text

    @property
    def _displayed_text(self) -> str:
        return self._widget.text()

    @_displayed_text.setter
    def _displayed_text(self, value: str):
        if self._displayed_text == value:
            return
        self._widget.setText(value)




