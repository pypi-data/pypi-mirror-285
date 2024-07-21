from typing import Protocol

from PyQt6.QtWidgets import QPlainTextEdit


class UiWidget(Protocol):
    _ui = ...


class TextDisplayProperty:
    def __init__(self, widget_name: str, ):
        self._widget_name = widget_name

    def __get_text_display(self, obj: UiWidget):
        try:
            return getattr(obj._ui, self._widget_name)
        except AttributeError:
            raise AttributeError(f'{type(self).__name__} not set correctly: ui.{self._widget_name} not found')

    def __get__(self, obj: UiWidget, owner) -> str:
        text_display = self.__get_text_display(obj)

        if isinstance(text_display, QPlainTextEdit):
            return text_display.toPlainText()

        return text_display.text()

    def __set__(self, obj: UiWidget, value):
        if self.__get__(obj, ...) == str(value):
            # Avoid deselection effect on line-edits
            return

        text_display = self.__get_text_display(obj)

        if isinstance(text_display, QPlainTextEdit):
            return text_display.setPlainText(str(value))

        text_display.setText(str(value))


__all__ = ['TextDisplayProperty']
