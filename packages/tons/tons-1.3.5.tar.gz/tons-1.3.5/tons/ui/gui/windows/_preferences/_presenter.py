import decimal
import os

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject
from pydantic import BaseModel

from ._model import PreferencesModel
from ._view import PreferencesView
from tons.ui.gui.windows.mixins.wallet_version_selection import WalletVersionSelectPresenter
from ...utils import slot_exc_handler


class ChangedFields(BaseModel):
    user_directory: bool
    api_key: bool
    version: bool
    network: bool
    scanner: bool
    testnet_api_key: bool
    dns_expiring_in: bool
    dns_refresh_amount: bool
    jetton_gas_amount: bool


class PreferencesPresenter(QObject, WalletVersionSelectPresenter):
    configuration_changed = pyqtSignal(ChangedFields)

    def __init__(self, model: PreferencesModel, view: PreferencesView):
        super().__init__()
        self._model: PreferencesModel = model
        self._view: PreferencesView = view
        self._display_model()
        self._view.setup_signals(self)

    def _display_model(self):
        self._display_concrete_model(self._model)

    def _display_concrete_model(self, model: PreferencesModel):
        self._view.user_directory = model.user_directory
        self._view.api_key = model.api_key
        default_version = model.default_wallet_version
        self._display_versions(default_version, add_default_version_hint=False)
        self._view.network = model.network
        self._view.testnet_api_key = model.testnet_api_key
        self._view.dns_expiring_in = model.dns_expiring_in
        self._view.dns_refresh_amount = model.dns_refresh_amount
        self._view.jetton_gas_amount = model.jetton_gas_amount
        self._view.scanner = model.scanner

    def _display_default_model(self):
        default_model = self._model.get_default_config_model()
        self._display_concrete_model(default_model)

    @property
    def _user_viewmodel_different(self) -> bool:
        fields = ['user_directory', 'api_key', 'version', 'network', 'testnet_api_key',
                  'dns_expiring_in', 'dns_refresh_amount', 'jetton_gas_amount', 'scanner']

        for field in fields:
            view_value = str(getattr(self._view, field))
            model_value = str(getattr(self._model, field))
            if view_value != model_value:
                return True

        return False

    def _calc_changed_fields(self) -> ChangedFields:
        fields = {field: False for field in ChangedFields.__fields__.keys()}

        for field in fields:
            view_value = str(getattr(self._view, field))
            model_value = str(getattr(self._model, field))
            if view_value != model_value:
                fields[field] = True

        return ChangedFields(**fields)

    @staticmethod
    def _user_directory_is_valid(path: str):
        return os.path.exists and os.path.isdir(path)

    @pyqtSlot()
    @slot_exc_handler()
    def on_viewmodel_updated(self):
        if self._user_viewmodel_different:
            self._view.notify_viewmodel_different()
        else:
            self._view.notify_viewmodel_unchanged()

    @pyqtSlot()
    @slot_exc_handler()
    def on_save(self):
        valid = True
        if not self._user_directory_is_valid(self._view.user_directory):
            self._view.notify_user_directory_invalid()
            valid = False

        try:
            decimal.Decimal(self._view.dns_refresh_amount)
        except decimal.InvalidOperation:
            self._view.notify_dns_refresh_amount_invalid()
            valid = False

        try:
            decimal.Decimal(self._view.jetton_gas_amount)
        except decimal.InvalidOperation:
            self._view.notify_jetton_amount_invalid()
            valid = False

        if not valid:
            return

        try:
            self._model.save(user_directory=self._view.user_directory,
                             api_key=self._view.api_key,
                             version=self._view.version,
                             network=self._view.network,
                             testnet_api_key=self._view.testnet_api_key,
                             dns_expiring_in=self._view.dns_expiring_in,
                             dns_refresh_amount=self._view.dns_refresh_amount,
                             jetton_gas_amount=self._view.jetton_gas_amount,
                             scanner=self._view.scanner)
        except:
            raise

        changed_fields = self._calc_changed_fields()
        self._view.close()
        self.configuration_changed.emit(changed_fields)

    @pyqtSlot()
    @slot_exc_handler()
    def on_restore_defaults(self):
        self._display_default_model()



