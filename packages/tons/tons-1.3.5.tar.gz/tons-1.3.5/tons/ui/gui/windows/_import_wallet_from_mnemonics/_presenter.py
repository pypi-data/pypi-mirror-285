from decimal import Decimal

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from tons.tonclient.utils import RecordNameInvalidError, InvalidMnemonicsError
from ._model import ImportWalletFromMnemonicsModel
from ._view import ImportWalletFromMnemonicsView
from tons.ui.gui.windows.mixins.wallet_info_service import WalletInfoServicePresenter
from ..mixins.keystore_selection import KeystoreSelectPresenter
from ..mixins.entity_name import InvalidNameNotification
from ..mixins.wallet_version_selection import WalletVersionSelectPresenter
from ..mixins.workchain_selection import WorkchainSelectPresenter
from ...utils import slot_exc_handler, pretty_balance, pretty_fiat_balance
from ._model import RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError


class ImportWalletFromMnemonicsPresenter(QObject, WalletInfoServicePresenter, KeystoreSelectPresenter,
                                         WalletVersionSelectPresenter, WorkchainSelectPresenter):
    created = pyqtSignal(str)  # keystore_name: str

    def __init__(self, model: ImportWalletFromMnemonicsModel, view: ImportWalletFromMnemonicsView):
        super().__init__()
        self._model: ImportWalletFromMnemonicsModel = model
        self._view: ImportWalletFromMnemonicsView = view
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
        mnemonics = self._view.mnemonics
        version = self._view.version
        workchain = self._view.workchain

        if mnemonics == '':
            self._view.hide_mnemonics_validation_error_notification()
            self._view.set_mnemonics_impressive_validity(False)
            self._view.set_mnemonics_validity(True)
            self._model.address = None
            return

        mnemonics_are_valid = self._model.can_be_mnemonics(mnemonics)
        self._view.set_mnemonics_impressive_validity(mnemonics_are_valid)
        if mnemonics_are_valid:
            address = self._model.address_from_mnemonics(mnemonics,
                                                         version,
                                                         workchain)
        else:
            address = None

        self._model.address = address

    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        try:
            self._model.create_wallet(self._view.wallet_name,
                                      self._view.comment,
                                      self._view.version,
                                      self._view.workchain,
                                      self._view.mnemonics
                                      )
        except RecordWithAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        except RecordWithNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except RecordNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        except InvalidMnemonicsError:
            self._view.notify_bad_mnemonics()
        else:
            self.created.emit(self._model.keystore_name)
            self._view.close()

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_keystore_changed(self, new_name: str):
        self._model.set_keystore(new_name)

    @property
    def _mnemonics_are_valid(self) -> bool:
        mnemonics = self._view.mnemonics
        mnemonics_are_valid = self._model.can_be_mnemonics(mnemonics)
        return mnemonics_are_valid

    def _display_model(self):
        self._display_versions()
        self._display_workchains()
        self._display_address_info()
        self._display_keystores()

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


__all__ = ['ImportWalletFromMnemonicsPresenter']