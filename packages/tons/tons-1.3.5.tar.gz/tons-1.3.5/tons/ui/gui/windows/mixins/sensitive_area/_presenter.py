import contextlib

from tons.tonclient.utils import BaseKeyStore
from tons.ui.gui.exceptions import KeystoreNotUnlocked
from tons.ui.gui.windows import DialogKeystoreWindow
from tons.ui.gui.windows._base import NormalView


class SensitiveAreaPresenterMixin:
    _view: NormalView

    @contextlib.contextmanager
    def keystore_sensitive(self, keystore: BaseKeyStore, message: str, title: str):
        try:
            self._unlock_keystore(keystore, message, title)
            yield
        finally:
            keystore.password = None

    def _unlock_keystore(self, keystore: BaseKeyStore, message: str, title: str):
        dialog = DialogKeystoreWindow(keystore, message, title)
        dialog.move_to_center(of=self._view)

        accepted = False

        def accept():
            nonlocal accepted
            accepted = True

        dialog.connect_accepted(accept)
        dialog.exec()

        if not accepted:
            raise KeystoreNotUnlocked

