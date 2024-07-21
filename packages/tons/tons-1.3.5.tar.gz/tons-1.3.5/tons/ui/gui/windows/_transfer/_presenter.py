from decimal import Decimal
from typing import Optional, List

from PyQt6.QtCore import QObject, pyqtSlot, Qt, pyqtSignal

from tons.tonclient.utils import WalletSecret
from tons.tonsdk.utils import Address
from tons.ui.gui.utils import SingleChildWindowManager, slot_exc_handler, xstr, TransferTask, LocalWhitelistLocation, \
    TransferEditAndRetryInfo
from ._model import TransferModel, RecordNotSelected, ContactNotSelected, InvalidBocFileError
from ._view import TransferView
from .._select_wallet import SelectWalletDestinationWindow, SelectWalletSourceWindow
from ..mixins.sensitive_area import SensitiveAreaPresenterMixin
from ..mixins.wallet_info_service import WalletInfoServicePresenter
from ...exceptions import GuiException, KeystoreNotUnlocked
from ...widgets import WalletListItemData


class TransferPresenter(QObject, WalletInfoServicePresenter, SensitiveAreaPresenterMixin):
    transfer_intent = pyqtSignal(TransferTask)
    contact_created = pyqtSignal(LocalWhitelistLocation)

    def __init__(self, model: TransferModel, view: TransferView):
        super().__init__()
        self._model: TransferModel = model
        self._view: TransferView = view
        self._view.setup_signals(self)

        self._select_from_window = SingleChildWindowManager()
        self._select_to_window = SingleChildWindowManager()

        self.init_wallet_info_service()

    @pyqtSlot()
    @slot_exc_handler()
    def on_address_info_changed(self):
        self._model.update_wallet_models_with_address_info()
        if self._model.wallet_from is not None:
            self._display_wallet_from(self._model.wallet_from)
        if self._model.wallet_to is not None:
            self._display_wallet_to(self._model.wallet_to)

    @pyqtSlot()
    @slot_exc_handler()
    def on_select_to_pressed(self):
        window = SelectWalletDestinationWindow(self._model.ctx, self._model.keystore_name)
        window.move_to_center(of=self._view)
        window.connect_selected(self.on_wallet_to_selected)
        window.connect_contact_created(self.on_contact_created)
        self._select_to_window.set(window)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_select_from_pressed(self):
        window = SelectWalletSourceWindow(self._model.ctx, self._model.keystore_name)
        window.move_to_center(of=self._view)
        window.connect_selected(self.on_wallet_from_selected)
        self._select_from_window.set(window)
        window.show()

    @pyqtSlot(WalletListItemData)
    @slot_exc_handler()
    def on_wallet_from_selected(self, wallet_list_item_data: WalletListItemData):
        self._select_wallet_from(wallet_list_item_data)

    @pyqtSlot(LocalWhitelistLocation)
    @slot_exc_handler()
    def on_contact_created(self, location: LocalWhitelistLocation):
        self.contact_created.emit(location)

    def _select_wallet_from(self, wallet_list_item_data: Optional[WalletListItemData]):
        self._display_wallet_from(wallet_list_item_data)
        self._view.hide_wallet_validity_notification()
        self._model.wallet_from = wallet_list_item_data

    @pyqtSlot(WalletListItemData)
    @slot_exc_handler()
    def on_wallet_to_selected(self, wallet_list_item_data: WalletListItemData):
        self._select_wallet_to(wallet_list_item_data)

    def _select_wallet_to(self, wallet_list_item_data: Optional[WalletListItemData]):
        self._display_wallet_to(wallet_list_item_data)
        self._view.display_default_transfer_message(wallet_list_item_data)
        self._view.hide_wallet_validity_notification()
        self._model.wallet_to = wallet_list_item_data

    def on_some_wallet_deleted(self, wallet_list_item_model: WalletListItemData):
        if wallet_list_item_model == self._model.wallet_to:
            self._select_wallet_to(None)
        if wallet_list_item_model == self._model.wallet_from:
            self._select_wallet_from(None)

    @pyqtSlot()
    @slot_exc_handler()
    def on_transfer_pressed(self):
        try:
            task = self._get_transfer_task()
        except (_BadUserInput, KeystoreNotUnlocked):
            return

        self.transfer_intent.emit(task)
        self._view.close()

    def _unlock_secret(self, amount, transfer_all_coins, recipient_name, sender) -> WalletSecret:
        assert self._sender_balance is not None
        amount = amount if not transfer_all_coins else self._sender_balance
        keystore = self._model.keystore
        message = f'Enter keystore password'
        title = f'Transfer {amount} TON to {recipient_name}'
        with self.keystore_sensitive(keystore, message, title):
            secret = keystore.get_secret(sender)
            return secret

    def _get_transfer_task(self) -> TransferTask:
        errors = False
        try:
            sender = self._model.record
        except RecordNotSelected:
            self._view.notify_wallet_from_not_selected()
            errors = True

        try:
            recipient = self._model.recipient
        except ContactNotSelected:
            self._view.notify_wallet_to_not_selected()
            errors = True

        if self._view.transfer_all_coins:
            amount = 0
        else:
            try:
                amount = Decimal(self._view.amount)
            except:
                self._view.notify_amount_invalid()
                errors = True

        state_init_cell = None
        try:
            state_init_cell = self._model.parse_boc(self._view.state_init_boc_path)
        except InvalidBocFileError as e:
            self._view.notify_state_init_path_invalid(e.message)
            errors = True
        else:
            self._view.hide_state_init_path_validity_notification()

        body_cell = None
        try:
            body_cell = self._model.parse_boc(self._view.body_boc_path)
        except InvalidBocFileError as e:
            self._view.notify_body_path_invalid(e.message)
            errors = True
        else:
            self._view.hide_body_path_validity_notification()

        message = self._view.message
        receiver_info = None
        if body_cell and message:
            self._view.notify_body_path_invalid("Can not be used with non-empty comment")
            errors = True
        elif self._view.encrypt_message:
            if body_cell:
                self._view.notify_body_path_invalid("Can not be used with encrypt comment flag")
                errors = True

            if not errors:
                receiver_info = self._model.ctx.ton_client.get_address_information(recipient.address)
                if not receiver_info.is_wallet:
                    self._view.notify_wallet_to_can_not_read_encrypted_messages()
                    errors = True

        if self._sender_balance is None:
            self._view.notify_wallet_from_balance_not_loaded()
            errors = True

        if errors:
            raise _BadUserInput

        secret = self._unlock_secret(amount, self._view.transfer_all_coins, recipient.name, sender)

        task = TransferTask(
            secret=secret,
            sender=sender,
            recipient=recipient,
            amount=amount,
            message=message,
            state_init=state_init_cell,
            body=body_cell,
            transfer_all_coins=self._view.transfer_all_coins,
            destroy_if_zero=self._view.destroy_if_zero,
            encrypt_message=self._view.encrypt_message,
            receiver_info=receiver_info,
            edit_and_retry_info=TransferEditAndRetryInfo(
                amount=amount,
                keystore_name=self._model.keystore_name,
                src=Address(sender.address),
                dst=Address(recipient.address),
                comment=message,
                encrypt_comment=self._view.encrypt_message,
                state_init_path=self._view.state_init_boc_path,
                body_path=self._view.body_boc_path,
                transfer_all_coins=self._view.transfer_all_coins,
                destroy_if_zero=self._view.destroy_if_zero
            )
        )
        return task

    @pyqtSlot(int)
    @slot_exc_handler()
    def on_check_box_transfer_all_state_changed(self, state: int):
        if state == Qt.CheckState.Checked.value:
            self._view.disable_amount_input()
            self._display_all_remaining_coins_if_checked()

        elif state == Qt.CheckState.Unchecked.value:
            self._view.enable_amount_input()
            self._view.amount = ''
        else:
            assert False

    def _display_all_remaining_coins_if_checked(self):
        if self._view.transfer_all_coins:
            try:
                self._view.amount = xstr(self._sender_balance)
            except AttributeError:
                self._view.amount = ''

    @property
    def _sender_balance(self) -> Optional[Decimal]:
        try:
            return self._model.wallet_from.address_info.balance
        except (AttributeError, TypeError):
            return None

    def _display_wallet_from(self, wallet: Optional[WalletListItemData]):
        self._view.display_wallet_from(wallet)
        self._display_all_remaining_coins_if_checked()

    def _display_wallet_to(self, wallet: Optional[WalletListItemData]):
        self._view.display_wallet_to(wallet)


class _BadUserInput(GuiException):
    def __init__(self):
        super().__init__('User has not provided valid transfer arguments')
