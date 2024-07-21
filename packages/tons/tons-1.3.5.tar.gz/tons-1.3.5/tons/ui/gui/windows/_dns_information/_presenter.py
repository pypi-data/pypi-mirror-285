from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from ._model import DnsInformationModel
from ._view import DnsInformationView
from .._base import ShowWalletInformationIntent
from ...utils import slot_exc_handler


class DnsInformationPresenter(QObject):
    show_wallet_information = pyqtSignal(ShowWalletInformationIntent)

    def __init__(self, model: DnsInformationModel, view: DnsInformationView):
        super().__init__()
        self._model: DnsInformationModel = model
        self._view: DnsInformationView = view
        view.setup_signals(self)
        self._display_model()

    def _display_model(self):
        self._view.domain = self._model.domain
        self._view.owner_wallet_name = self._model.owner_wallet_name
        self._view.owner_wallet_address = self._model.owner_wallet_address
        self._view.expires = self._model.expires
        self._view.expires_in = self._model.expires_in
        self._view.ownership_status = self._model.ownership_status
        self._view.contract_address = self._model.contract_address

    @pyqtSlot()
    @slot_exc_handler()
    def on_wallet_label_clicked(self):
        self.show_wallet_information.emit(self._show_wallet_info_intent)

    @property
    def _show_wallet_info_intent(self) -> ShowWalletInformationIntent:
        return ShowWalletInformationIntent(keystore=self._model.keystore,
                                           record=self._model.record)




