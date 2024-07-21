from typing import Optional

from tons.tonclient.utils import BaseKeyStore

from ._model import DialogKeystorePasswordModel
from ._view import DialogKeystorePasswordView
from ._presenter import DialogKeystorePresenter

from .._base import DialogWindow


class DialogKeystoreWindow(DialogWindow):
    def __init__(self,
                 keystore: BaseKeyStore,
                 message: Optional[str] = None,
                 title: Optional[str] = None):
        super().__init__()
        self._model = DialogKeystorePasswordModel(keystore)
        self._view = DialogKeystorePasswordView()
        self._view.setWindowTitle(title)
        self._view.message = message
        self._view.keystore_name = keystore.short_name
        self._presenter = DialogKeystorePresenter(self._model, self._view)

    def connect_accepted(self, slot):
        self._view.accepted.connect(slot)

