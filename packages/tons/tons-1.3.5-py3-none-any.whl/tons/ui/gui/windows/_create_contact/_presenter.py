from decimal import Decimal

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from pydantic import ValidationError

from tons.tonclient.utils import WhitelistContactNameInvalidError, \
    WhitelistContactNameAlreadyExistsError, WhitelistContactAddressAlreadyExistsError
from tons.tonsdk.utils import InvalidAddressError
from ._model import CreateContactModel
from ._view import CreateContactView
from tons.ui.gui.windows.mixins.wallet_info_service import WalletInfoServicePresenter
from ..components.entity_name import InvalidNameNotification
from ..components.whitelists import WhitelistsPresenterComponent
from ...utils import pretty_balance, pretty_fiat_balance, slot_exc_handler, show_in_scanner, ContactLocation


class CreateContactPresenter(QObject, WalletInfoServicePresenter):
    created = pyqtSignal(ContactLocation)

    def __init__(self, model: CreateContactModel, view: CreateContactView):
        super().__init__()
        self._model: CreateContactModel = model
        self._view: CreateContactView = view
        self._whitelists = WhitelistsPresenterComponent(self._view.whitelists, self._model.whitelists)
        self._display_model()
        self.set_default_contact_name()
        view.setup_signals(self)
        self.init_wallet_info_service()
        self.set_default_contact_name()

    def _display_address_info(self):
        address_info = self._model.address_info
        if address_info is None:
            return self._display_none_address_info()

        self._view.balance = pretty_balance(address_info.balance)
        self._view.balance_fiat = pretty_fiat_balance(self._model.balance_fiat, self._model.fiat_symbol)

    def _display_none_address_info(self):
        self._view.balance = '00.00'
        self._view.balance_fiat = pretty_fiat_balance(Decimal(0), self._model.fiat_symbol)

    def _display_model(self):
        self._display_address_info()
        self._whitelists.display()

    def set_default_contact_name(self):
        default_contact_name = self._model.get_default_contact_name(self._view.whitelists.selected_location)
        self._view.contact_name = default_contact_name

    @pyqtSlot()
    @slot_exc_handler()
    def on_user_changed_wallet_info(self):
        address = self._view.address
        if self._model.address_is_valid(address):
            self._model.address = address
            self._view.set_address_impressive_validity(True)
        else:
            self._model.address = None
            self._view.set_address_impressive_validity(False)

    @pyqtSlot()
    @slot_exc_handler()
    def on_address_info_changed(self):
        self._display_address_info()

    @pyqtSlot()
    @slot_exc_handler()
    def on_show_in_scanner(self):
        address = self._view.address
        if not self._model.address_is_valid(address):
            self._view.set_address_validity(False)
            return

        show_in_scanner(address, self._model.network_is_testnet, self._model.scanner)

    @pyqtSlot()
    @slot_exc_handler()
    def on_create(self):
        contact_name = self._view.contact_name
        default_message = self._view.default_message
        address = self._view.address
        location = self._view.whitelists.selected_location

        try:
            self._model.create_contact(location, contact_name, address, default_message)
        except (InvalidAddressError, ValidationError):
            self._view.notify_invalid_address()
        except WhitelistContactAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        except WhitelistContactNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        except WhitelistContactNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        else:
            self.created.emit(location)
            self._view.close()
