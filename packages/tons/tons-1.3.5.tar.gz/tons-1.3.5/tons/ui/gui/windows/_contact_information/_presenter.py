from typing import List

from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from tons.tonclient.utils import WhitelistContactNameAlreadyExistsError, WhitelistContactAddressAlreadyExistsError
from tons.tonsdk.utils import InvalidAddressError, Address
from ._view import ContactInformationView
from ._model import ContactInformationModel, AddressTypeEnum
from .._dialog_qr import DialogQRWindow
from ..components.entity_name import InvalidNameNotification
from ..components.whitelists import WhitelistsPresenterComponent
from ..mixins.wallet_info_service import WalletInfoServicePresenter
from ...utils import pretty_balance, slot_exc_handler, copy_to_clipboard, pretty_fiat_balance, ContactLocation, \
    workchain_with_hint_text


class ContactInformationPresenter(QObject, WalletInfoServicePresenter):
    edited = pyqtSignal([ContactLocation, ContactLocation])

    def __init__(self, model: ContactInformationModel, view: ContactInformationView):
        super().__init__()
        self._model: ContactInformationModel = model
        self._view: ContactInformationView = view

        view.setup_signals(self)
        self.init_wallet_info_service()
        self._whitelists = WhitelistsPresenterComponent(self._view.whitelists, self._model.whitelists)

        self._display_model()

    def _display_contact(self):
        contact = self._model.contact
        self._view.contact_name = contact.name
        self._view.default_message = contact.default_message
        self._view.workchain = workchain_with_hint_text(Address(contact.address).wc)
        self._view.address = contact.address
        self._display_additional_addresses()

    def _display_additional_addresses(self):
        try:
            morph = self._model.morph_additional_address_types(self._view.address)
        except InvalidAddressError:
            self._view.hide_additional_addresses()
            return

        for idx, (address_type, address) in enumerate(morph):
            address_label = self._readable_address_type(address_type)
            self._view.set_additional_address(address, idx)
            self._view.set_additional_address_label(address_label, idx)

    def _display_address_info(self):
        address_info = self._model.address_info
        if address_info is None:
            return self._display_none_address_info()

        self._view.balance = pretty_balance(address_info.balance)
        self._view.balance_fiat = pretty_fiat_balance(self._model.balance_fiat, self._model.fiat_symbol)
        self._view.last_activity = address_info.last_activity_datetime or ''
        self._view.ton_symbol.show()

    def _display_none_address_info(self):
        self._view.balance = '00.00'
        self._view.last_activity = ''
        self._view.balance_fiat = ''

    def _display_location(self):
        location = self._model.location
        self._view.whitelists.set_location(location)

    def _display_model(self):
        self._display_contact()
        self._display_address_info()
        self._whitelists.display()
        self._display_location()

    @property
    def _user_viewmodel_different(self) -> bool:
        user_viewmodel: List[str] = [
            self._view.contact_name,
            self._view.default_message,
            self._view.address,
            self._view.whitelists.selected_location
        ]
        model: List[str] = [
            self._model.contact.name,
            self._model.contact.default_message,
            self._model.contact.address,
            self._model.location
        ]
        return user_viewmodel != model

    @staticmethod
    def _readable_address_type(address_type: AddressTypeEnum):
        matrix = {
            address_type.raw: 'Raw',
            address_type.bounceable: 'Bounceable',
            address_type.nonbounceable: 'Nonbounceable'
        }
        return matrix[address_type]

    # region
    # ================ Model slots ================
    @pyqtSlot()
    @slot_exc_handler
    def on_address_info_changed(self):
        self._display_address_info()
    # endregion

    # region
    # ================ View slots ================

    @pyqtSlot()
    @slot_exc_handler()
    def on_address_edited(self):
        if not self._model.address_invalid(self._view.address):
            self._view.notify_address_valid()
        self._display_additional_addresses()
        self._model.address = self._view.address

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_bounceable_address(self):
        copy_to_clipboard(self._view.address_bounceable)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_nonbounceable_address(self):
        copy_to_clipboard(self._view.address_nonbounceable)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_address(self):
        copy_to_clipboard(self._view.address)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_address_type_2(self):
        copy_to_clipboard(self._view.address_type_2)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_address_type_3(self):
        copy_to_clipboard(self._view.address_type_3)

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_address_code(self):
        copy_to_clipboard(self._model.address_code)

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_address_data(self):
        copy_to_clipboard(self._model.address_data)

    @pyqtSlot()
    @slot_exc_handler()
    def on_show_qr_pressed(self):
        dialog = DialogQRWindow(self._view.address)
        dialog.move_to_center(of=self._view)
        dialog.exec()

    @pyqtSlot()
    @slot_exc_handler()
    def on_viewmodel_updated(self):
        if self._user_viewmodel_different:
            self._view.notify_viewmodel_different()
        else:
            self._view.notify_viewmodel_unchanged()

    def on_whitelist_changed(self, location: ContactLocation):
        self.on_viewmodel_updated()

    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        if self._model.address_invalid(self._view.address):
            self._view.notify_address_invalid()
            return

        if self._view.contact_name == '':
            self._view.notify_invalid_name(InvalidNameNotification.empty)
            return

        old_location = self._model.location
        new_location = self._view.whitelists.selected_location
        try:
            if old_location == new_location:
                self._model.edit_contact(self._view.contact_name,
                                         self._view.address,
                                         self._view.default_message)
            else:
                self._model.move_contact(self._view.contact_name,
                                         self._view.address,
                                         self._view.default_message,
                                         new_location)
        except WhitelistContactNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except WhitelistContactAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        else:
            self.edited.emit(old_location, new_location)
            self._view.close()
