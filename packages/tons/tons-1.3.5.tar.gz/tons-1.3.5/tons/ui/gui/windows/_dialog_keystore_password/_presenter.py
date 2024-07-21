from typing import Protocol

from PyQt6.QtCore import pyqtSlot, QObject

from ._model import KeyStoreInvalidPasswordError
from ...utils import slot_exc_handler


class Model(Protocol):
    def enter_sensitive(self, secret: str): ...


class View(Protocol):
    password: str
    def setup_signals(self, presenter): ...
    def notify_wrong_password(self): ...
    def close_success(self): ...


class DialogKeystorePresenter(QObject):
    def __init__(self, model: Model, view: View):
        super().__init__()
        self._model = model
        self._view = view
        view.setup_signals(self)

    @pyqtSlot()
    @slot_exc_handler()
    def on_password_entered(self):
        try:
            self._model.enter_sensitive(self._view.password)
        except KeyStoreInvalidPasswordError:
            self._view.notify_wrong_password()
        else:
            self._view.close_success()


