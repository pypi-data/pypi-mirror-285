from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from tons.tonclient.utils import RecordNameInvalidError
from ._model import CreateWalletModel
from ._view import CreateWalletView
from ..mixins.keystore_selection import KeystoreSelectPresenter
from ..mixins.entity_name import InvalidNameNotification
from ..mixins.wallet_version_selection import WalletVersionSelectPresenter
from ..mixins.workchain_selection import WorkchainSelectPresenter
from ...utils import slot_exc_handler
from ._model import RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError


class CreateWalletPresenter(QObject, KeystoreSelectPresenter,
                            WalletVersionSelectPresenter, WorkchainSelectPresenter):
    created = pyqtSignal(str)  # keystore_name: str

    def __init__(self, model: CreateWalletModel, view: CreateWalletView):
        super().__init__()
        self._model: CreateWalletModel = model
        self._view: CreateWalletView = view
        self._display_model()
        view.setup_signals(self)
        self.set_default_wallet_name()

    def set_default_wallet_name(self):
        self._view.wallet_name = self._model.default_wallet_name


    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        try:
            self._model.create_wallet(self._view.wallet_name,
                                      self._view.comment,
                                      self._view.version,
                                      self._view.workchain)
        except RecordWithAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        except RecordWithNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except RecordNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        else:
            self.created.emit(self._model.keystore_name)
            self._view.close()

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_keystore_changed(self, new_name: str):
        self._model.set_keystore(new_name)

    def _display_model(self):
        self._display_versions()
        self._display_workchains()
        self._display_keystores()


__all__ = ['CreateWalletPresenter']