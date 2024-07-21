import pathlib
from decimal import Decimal

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from tons.logging_ import tons_logger
from tons.tonclient.utils import RecordNameInvalidError
from tons.tonsdk.crypto.exceptions import InvalidPrivateKeyError
from ._model import ImportWalletFromPrivateKeyModel, PrivateKeyNotSelected
from ._view import ImportWalletFromPrivateKeyView
from tons.ui.gui.windows.mixins.wallet_info_service import WalletInfoServicePresenter
from ..mixins.keystore_selection import KeystoreSelectPresenter
from ..mixins.entity_name import InvalidNameNotification
from ..mixins.wallet_version_selection import WalletVersionSelectPresenter
from ..mixins.workchain_selection import WorkchainSelectPresenter
from ...utils import slot_exc_handler, pretty_balance, pretty_fiat_balance
from ._model import RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError


class ImportWalletFromPrivateKeyPresenter(QObject, WalletInfoServicePresenter, KeystoreSelectPresenter,
                                         WalletVersionSelectPresenter, WorkchainSelectPresenter):
    created = pyqtSignal(str)  # keystore_name: str

    def __init__(self, model: ImportWalletFromPrivateKeyModel, view: ImportWalletFromPrivateKeyView):
        super().__init__()
        self._model: ImportWalletFromPrivateKeyModel = model
        self._view: ImportWalletFromPrivateKeyView = view
        self._display_model()
        view.setup_signals(self)
        self.set_default_wallet_name()
        self.init_wallet_info_service()

    def set_default_wallet_name(self):
        self._view.wallet_name = self._model.default_wallet_name

    @pyqtSlot()
    @slot_exc_handler
    def on_address_info_changed(self):
        self._display_address_info()

    @pyqtSlot()
    @slot_exc_handler()
    def on_user_changed_wallet_info(self):
        self._model.set_wallet_model_info(self._view.version, self._view.workchain)

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_pk_path_selected(self, pk_path: str):
        try:
            self._model.set_private_key_path(pk_path)
        except InvalidPrivateKeyError as exc:
            self._view.notify_invalid_pk()
        except OSError as exc:
            tons_logger().warning("OSError while reading private key path: " + str(exc))
        else:
            p = pathlib.Path(pk_path)
            self._view.pk_path = p.name
            if not self._view.name_edited:
                self._view.wallet_name = p.stem

    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        try:
            self._model.create_wallet(self._view.wallet_name,
                                      self._view.comment)
        except RecordWithAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        except RecordWithNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except RecordNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        except InvalidPrivateKeyError:
            self._view.notify_invalid_pk()
        except PrivateKeyNotSelected:
            self._view.notify_invalid_pk('Please select a private key file')
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
        self._display_address_info()
        self._display_keystores()
        self._view.pk_path = ''

    def _display_address_info(self):
        address_info = self._model.address_info
        if address_info is None:
            return self._display_none_address_info()

        self._view.balance = pretty_balance(address_info.balance)
        self._view.balance_fiat = pretty_fiat_balance(self._model.balance_fiat, self._model.fiat_symbol)
        self._view.last_activity = address_info.last_activity_datetime or ''

    def _display_none_address_info(self):
        self._view.last_activity = ''
        self._view.balance = '00.00'
        self._view.balance_fiat = pretty_fiat_balance(Decimal(0), self._model.fiat_symbol)


__all__ = ['ImportWalletFromPrivateKeyPresenter']