import functools
from typing import List, Optional

from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from tons.tonsdk.utils import Address
from ._view import WalletInformationView
from ._model import WalletInformationModel, RecordNameInvalidError, \
    RecordWithAddressAlreadyExistsError, RecordWithNameAlreadyExistsError, MnemonicsNotPresent
from .._dialog_keystore_password import DialogKeystoreWindow
from .._dialog_qr import DialogQRWindow
from ..mixins.keystore_selection import KeystoreSelectPresenter
from ..mixins.sensitive_area import SensitiveAreaPresenterMixin
from ..mixins.wallet_info_service import WalletInfoServicePresenter
from ..mixins.entity_name import InvalidNameNotification
from ...exceptions import KeystoreNotUnlocked
from ...utils import xstr, pretty_balance, slot_exc_handler, copy_to_clipboard, wallet_state_with_circle, \
    pretty_fiat_balance, workchain_with_hint_text


class WalletInformationPresenter(QObject, WalletInfoServicePresenter, KeystoreSelectPresenter,
                                 SensitiveAreaPresenterMixin):
    edited = pyqtSignal(str)  # keystore name: str

    def __init__(self, model: WalletInformationModel, view: WalletInformationView):
        super().__init__()
        self._model: WalletInformationModel = model
        self._view: WalletInformationView = view

        view.setup_signals(self)

        self.init_wallet_info_service()
        self._display_model()

    def _display_record(self):
        record = self._model.record

        self._view.wallet_name = record.name
        self._view.comment = record.comment

        self._view.address_bounceable = Address(record.address).to_string(True, True, True)
        self._view.address_nonbounceable = Address(record.address).to_string(True, True, False)
        self._view.address_raw = Address.raw_id(record.address)
        self._view.version = record.version
        self._view.workchain = workchain_with_hint_text(record.workchain)

        self._view.subwallet_id = record.subwallet_id

    def _display_address_info(self):
        address_info = self._model.address_info
        if address_info is None:
            return self._display_none_address_info()

        self._view.balance = pretty_balance(address_info.balance)
        self._view.balance_fiat = pretty_fiat_balance(self._model.balance_fiat, self._model.fiat_symbol)
        self._view.last_activity = address_info.last_activity_datetime or ''
        self._view.state = wallet_state_with_circle(address_info.state)
        self._view.contract_type = xstr(address_info.contract_type)
        self._view.seqno = xstr(address_info.seqno)

    def _display_none_address_info(self):
        self._view.balance = '00.00'
        [self._view.state,
         self._view.contract_type,
         self._view.seqno,
         self._view.last_activity] = [''] * 4
        self._view.balance_fiat = ''

    def _display_model(self):
        self._display_record()
        self._display_address_info()
        self._display_keystores()

    def _user_viewmodel_different(self):
        user_viewmodel: List[str] = [
            self._view.wallet_name,
            self._view.comment,
        ]
        model: List[str] = [
            self._model.record.name,
            self._model.record.comment,
        ]
        keystore_different = self._view.different_keystore_is_selected
        return (user_viewmodel != model) or keystore_different

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
    @slot_exc_handler
    def on_copy_bounceable_address(self):
        copy_to_clipboard(self._view.address_bounceable)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_nonbounceable_address(self):
        copy_to_clipboard(self._view.address_nonbounceable)

    @pyqtSlot()
    @slot_exc_handler
    def on_copy_raw_address(self):
        copy_to_clipboard(self._view.address_raw)

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_mnemonics(self):
        copy_to_clipboard(self._view.mnemonics)

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_address_code(self):
        copy_to_clipboard(self._model.address_code)

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_address_data(self):
        copy_to_clipboard(self._model.address_data)

    @pyqtSlot()
    @slot_exc_handler
    def on_show_mnemonics_pressed(self):
        try:
            with self.keystore_sensitive(self._model.keystore,
                                         message='To show the mnemonics enter keystore password',
                                         title=f'Show {self._model.record.name} mnemonics'):
                self._reveal_mnemonics()
        except KeystoreNotUnlocked:
            return

    @pyqtSlot()
    @slot_exc_handler()
    def on_show_qr_pressed(self):
        dialog = DialogQRWindow(self._view.address_bounceable)
        dialog.move_to_center(of=self._view)
        dialog.exec()

    @pyqtSlot()
    @slot_exc_handler()
    def _reveal_mnemonics(self):
        try:
            self._view.mnemonics = self._model.get_mnemonics()
        except MnemonicsNotPresent:
            self._view.notify_mnemonics_not_present()
        else:
            self._view.show_mnemonics()

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_keystore_changed(self, _name: str):
        self.on_viewmodel_updated()

    @pyqtSlot()
    @slot_exc_handler()
    def on_viewmodel_updated(self):
        if self._user_viewmodel_different():
            self._view.notify_viewmodel_different()
        else:
            self._view.notify_viewmodel_unchanged()

    @pyqtSlot()
    @slot_exc_handler()
    def on_save_clicked(self):
        new_name = self._view.wallet_name
        new_comment = self._view.comment
        new_keystore_name = self._view.current_keystore_name

        if self._view.different_keystore_is_selected:
            try:
                with self.keystore_sensitive(self._model.keystore,
                                                     message=f'To move the wallet enter the password for<br>'
                                                             f'<b>{self._model.keystore_name}</b> keystore.',
                                                     title=f'Move {self._model.record.name} wallet',
                                                     ):
                    self._save(new_name, new_comment, new_keystore_name)
            except KeystoreNotUnlocked:
                return

        else:
            self._save(new_name, new_comment)

    @slot_exc_handler()
    def _save(self, new_name: str, new_comment: str, new_keystore_name: Optional[str] = None):
        keystore_name = self._model.keystore_name
        try:
            self._model.save(new_name, new_comment, new_keystore_name)
        except RecordWithAddressAlreadyExistsError as exception:
            self._view.notify_address_already_exists(exception.name)
        except RecordWithNameAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except RecordNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        else:
            self.on_viewmodel_updated()
            self.edited.emit(keystore_name)

            moved = new_keystore_name is not None
            if moved:
                self._display_keystores()
                self.edited.emit(new_keystore_name)

            self._view.close()

    # end region
