import os
import sys
from functools import wraps, lru_cache
from json import JSONDecodeError
from typing import List, Sequence, Callable, Optional, Union

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QApplication

from tons import settings
from tons.logging_ import tons_logger
from tons.tonclient.utils import Record, WhitelistContact, WhitelistContactNameAlreadyExistsError, \
    WhitelistContactAddressAlreadyExistsError, WhitelistContactNameInvalidError, BaseKeyStore
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, \
    RecordDoesNotExistError, RecordNameInvalidError, InvalidKeyStoreError, InvalidBackupError
from tons.tonclient.utils._keystores import KeystoreBackup
from tons.ui._utils import get_recipient_by_address, RecipientKind
from ._model import MainWindowModel, KeyStoreNotSelected
from ._view import MainWindowView
from .. import ImportKeystoreWindow, CreateWalletWindow
from .._dns_information import DnsInformationWindow
from .._import_wallet_from_pk import ImportWalletFromPrivateKeyWindow
from .._transactions_history import TransactionsHistoryWindow
from .._base import DeleteWalletSensitiveWindow, ShowWalletInformationIntent
from .._preferences import PreferencesWindow
from .._contact_information import ContactInformationWindow
from .._create_batch_wallet import CreateBatchWalletWindow
from .._create_contact import CreateContactWindow
from .._create_keystore import CreateKeystoreWindow
from .._import_wallet_from_mnemonics import ImportWalletFromMnemonicsWindow
from .._preferences import ChangedFields
from .._transfer import TransferWindow
from .._transfer._window import TransferPreSelectedInfo
from .._wallet_information import WalletInformationWindow
from ..components.contact_kind_filter import ContactKindFilter
from ..components.status_bar import StatusBarMessageModel
from ..mixins.list_dns import ListDnsPresenter, validate_dns_non_skeleton
from ..mixins.list_wallets import ListWalletsPresenter
from ...exceptions import KeystoreNotUnlocked, GuiException
from ...utils import slot_exc_handler, SingleChildWindowManager, show_message_box_warning, \
    ContactLocation, GlobalWhitelistLocation, show_system_notification, LocalWhitelistLocation, show_in_scanner, \
    show_message_box_critical, ErrorNotification, copy_to_clipboard, EditAndRetryInfo, \
    TransferEditAndRetryInfo
from ...utils import SystemNotification
from ...widgets import SideBarListItemModel, WalletListItemKind, WalletListItemData, SideBarListItemKind, \
    WalletContextMenuView, WalletContextMenuModel, WalletMoveToLocation, WalletMoveToLocationKind, \
    RefreshDnsMenuModel, DnsListItemData
from ...widgets._dns_context_menu import DnsContextMenuView, DnsContextMenuModel

_KEYSTORE_EXT = settings.KEYSTORE_FILE_EXT
_EXPORTED_KEYSTORE_EXT = '.json'
_EXPORT_MIME_FILTER = f"Keystore unencrypted backup (*{_EXPORTED_KEYSTORE_EXT})"
_BACKUP_MIME_FILTER = f"Keystore (*{_KEYSTORE_EXT})"
_IMPORT_KEYSTORE_MIME_FILTER = f"Keystore backup (*{_EXPORTED_KEYSTORE_EXT}; *{_KEYSTORE_EXT})"
_ALL_MIME_FILTER = f"All files (*)"


@lru_cache
def _default_file_save_directory():
    return os.path.expanduser('~')


class ChildWindows:
    def __init__(self):
        self.wallet_info = SingleChildWindowManager()
        self.contact_info = SingleChildWindowManager()
        self.create_wallet = SingleChildWindowManager()
        self.create_keystore = SingleChildWindowManager()
        self.create_contact = SingleChildWindowManager()
        self.preferences = SingleChildWindowManager()
        self.transfer = SingleChildWindowManager()
        self.import_keystore_backup = SingleChildWindowManager()
        self.transactions_history = SingleChildWindowManager()
        self.dns_information = SingleChildWindowManager()

    def all_windows(self) -> List[SingleChildWindowManager]:
        result = []
        for var in vars(self):
            result.append(getattr(self, var))
        return result


def _show_keystore_not_selected_warning():
    show_message_box_warning("Select the keystore first!", "Select the keystore first!")


def _require_keystore_selected(method: Callable):
    @wraps(method)
    def magic(self: 'MainWindowPresenter', *args, **kwargs):
        if not self._keystore_is_selected:
            return _show_keystore_not_selected_warning()
        return method(self, *args, **kwargs)

    return magic


class _UnknownKeystoreFileContent(GuiException):
    pass


class MainWindowPresenter(QObject, ListWalletsPresenter, ListDnsPresenter):
    _system_notify = pyqtSignal(SystemNotification)

    def __init__(self, model: MainWindowModel, view: MainWindowView):
        super().__init__()
        self._model: MainWindowModel = model
        self._model.setup_signals(self)
        self._view: MainWindowView = view
        self._view.setup_signals(self)
        self._view.change_to_empty_subcontext()

        self._display_model()
        self._child_windows = ChildWindows()
        self._model.setup_signals(self)

        self._load_all_keystores_and_upgrade()
        self.init_list_wallets()

        self._wallet_context_menu = WalletContextMenuView(parent=self._view)
        self._wallet_context_menu.setup_signals(self)

        self._dns_context_menu = DnsContextMenuView(parent=self._view)
        self._dns_context_menu.setup_signals(self)

        self._setup_signals()

    def setup_app(self):
        self._check_updates()
        self._ensure_directories_exist()

    def _load_all_keystores_and_upgrade(self):
        try:
            keystores = self._model.load_and_upgrade_all_keystores()
        except InvalidKeyStoreError as exc:
            show_message_box_critical("Failed to load keystore", str(exc), self._on_critical_error_message_box_finished)
            return
        self._show_keystores_upgrade_info(keystores)
        self._model.init_keystores()
        self._display_keystores()

    def _on_critical_error_message_box_finished(self, result: int):
        sys.exit(-1)

    def _check_updates(self):
        if self._model.tons_is_outdated():
            self._view.set_outdated()
            if self._model.ctx.config.tons.warn_if_outdated:
                self._view.warn_outdated()

    def _ensure_directories_exist(self):
        try:
            self._model.ensure_directories_exist()
        except (PermissionError, OSError) as e:
            self._view.warn_workdir_error(e.filename)
            self._show_preferences()

    def _setup_signals(self):
        self._system_notify.connect(self.on_system_notification)
        self._dns_refresh_intent.connect(self._model.background_task_service.on_dns_tasks)

    def _display_model(self):
        self._display_keystores()
        self._display_whitelists()
        self._display_wallets()
        self._display_dns()
        self._display_refresh_dns_menu()

    def _display_keystores(self):
        keystores: Sequence[SideBarListItemModel] = self._model.keystores_models
        self._view.set_keystores(keystores)

    def _display_whitelists(self):
        whitelists: Sequence[SideBarListItemModel] = [self._model.global_whitelist_sidebar_model]
        self._view.set_whitelists(whitelists)

    def _display_wallets(self):
        if self._view.selected_sidebar_item is None:
            wallet_items = []
        else:
            wallet_items = self._model.get_all_wallets()
        self._view.set_wallet_items(wallet_items)
        self._view.display_wallet_count(wallet_items)
        self._view.set_total_balance(self._model.total_ton_balance)
        self._view.update_wallets_obscurity()

    def _display_dns(self):
        if self._view.selected_sidebar_item is None:
            all_loaded, dns_items, dns_count = False, {}, 0
        else:
            all_loaded, dns_items, dns_count = self._model.get_all_dns()

        self._view.set_dns_items(dns_items, all_loaded, dns_count)
        self._view.display_dns_count(dns_count, all_loaded)
        self._view.update_dns_buttons_availability(all_loaded)
        self._view.update_dns_obscurity()

    @pyqtSlot(SideBarListItemModel)
    @slot_exc_handler()
    def on_sidebar_item_selected(self, sidebar_item: SideBarListItemModel):
        self._view.display_all_items_count = {
            SideBarListItemKind.password_keystore: False,
            SideBarListItemKind.global_whitelist: True
        }[sidebar_item.kind]

        if sidebar_item.kind == SideBarListItemKind.password_keystore:
            keystore_name = sidebar_item.name
            self._model.set_keystore(keystore_name)
            self._display_wallets()
            self._view.reset_dns_items()
            self._display_dns()
            self._view.change_to_correct_subcontext()
            self._view.set_keystore_name(keystore_name)
            self._view.show_all_buttons()
        elif sidebar_item.kind == SideBarListItemKind.global_whitelist:
            self._model.set_keystore(None)
            self._view.set_global_whitelist_subcontext()
            self._display_wallets()
            self._view.set_global_whitelist_name()
            self._view.hide_unnecessary_buttons(necessary_kind=ContactKindFilter.all_items)
        else:
            raise NotImplementedError

    @pyqtSlot()
    @slot_exc_handler()
    def on_wallet_selected(self):
        selected_wallet_model = self._view.selected_wallet_model
        assert isinstance(selected_wallet_model, WalletListItemData)
        if selected_wallet_model.kind == WalletListItemKind.record:
            self._show_wallet_information_window_from_list(selected_wallet_model)
        elif selected_wallet_model.kind in (WalletListItemKind.local_contact, WalletListItemKind.global_contact):
            self._show_contact_information_window_from_list(selected_wallet_model)
        else:
            raise NotImplementedError(f"Unknown wallet kind: {selected_wallet_model.kind}")

    @pyqtSlot()
    @slot_exc_handler()
    @validate_dns_non_skeleton
    def on_dns_selected(self):
        selected_dns_model = self._view.selected_dns_model
        assert isinstance(selected_dns_model, DnsListItemData)
        self._show_dns_information_window_from_list(selected_dns_model)

    @pyqtSlot()
    @slot_exc_handler()
    def on_address_info_changed(self):
        ListWalletsPresenter.on_address_info_changed(self)
        self._view.set_total_balance(self._model.total_ton_balance)

    @pyqtSlot()
    @slot_exc_handler()
    def on_dns_info_changed(self):
        self._display_dns()

    @_require_keystore_selected
    def _show_dns_information_window_from_list(self, selected_dns_model: DnsListItemData):
        selected_keystore = self._model.keystore
        record = self._model.keystore.get_record_by_address(selected_dns_model.wallet_address)

        window = DnsInformationWindow(self._model.ctx, selected_dns_model, selected_keystore, record)
        window.connect_show_wallet_information(self._show_wallet_information_window)
        self._child_windows.dns_information.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @_require_keystore_selected
    def _show_wallet_information_window_from_list(self, selected_wallet_model: WalletListItemData):
        assert selected_wallet_model.kind == WalletListItemKind.record
        self._show_wallet_information_window(ShowWalletInformationIntent(
            keystore=self._model.keystore,
            record=selected_wallet_model.entity
        ))

    @pyqtSlot(ShowWalletInformationIntent)
    @slot_exc_handler()
    def _show_wallet_information_window(self, intent: ShowWalletInformationIntent):
        window = WalletInformationWindow(self._model.ctx, intent.keystore, intent.record)
        self._child_windows.wallet_info.set(window)
        window.connect_edited(self._on_keystore_modified)
        window.move_to_center(of=self._view)
        window.show()

    def _show_contact_information_window_from_list(self, selected_wallet_model: WalletListItemData):
        assert selected_wallet_model.kind in (WalletListItemKind.local_contact, WalletListItemKind.global_contact)
        try:
            selected_keystore = self._model.keystore
        except KeyStoreNotSelected:
            selected_keystore = None

        selected_contact = selected_wallet_model.entity

        if selected_wallet_model.kind == WalletListItemKind.local_contact:
            location = LocalWhitelistLocation(selected_keystore.short_name)
        else:
            location = GlobalWhitelistLocation()

        window = ContactInformationWindow(self._model.ctx, selected_contact, location)
        window.connect_edited(self._on_contact_edited)
        self._child_windows.contact_info.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_obscurity_changed(self):
        if self._view.sensitive_data_obscure:
            self._child_windows.transactions_history.close()

    @pyqtSlot()
    @slot_exc_handler()
    @_require_keystore_selected
    def on_new_wallet(self):
        selected_keystore = self._model.keystore
        window = CreateWalletWindow(self._model.ctx, selected_keystore)
        window.connect_created(self._on_keystore_modified)
        self._child_windows.create_wallet.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    @_require_keystore_selected
    def on_import_from_mnemonics(self):
        selected_keystore = self._model.keystore
        window = ImportWalletFromMnemonicsWindow(self._model.ctx, selected_keystore)
        window.connect_created(self._on_keystore_modified)
        self._child_windows.create_wallet.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    @_require_keystore_selected
    def on_import_from_private_key(self):
        selected_keystore = self._model.keystore
        window = ImportWalletFromPrivateKeyWindow(self._model.ctx, selected_keystore)
        window.connect_created(self._on_keystore_modified)
        self._child_windows.create_wallet.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    @_require_keystore_selected
    def on_create_batch(self):
        selected_keystore = self._model.keystore
        window = CreateBatchWalletWindow(self._model.ctx, selected_keystore)
        window.connect_created(self._on_keystore_modified)
        self._child_windows.create_wallet.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_create_keystore(self):
        window = CreateKeystoreWindow(self._model.ctx)
        window.connect_created(self._on_keystore_created)
        self._child_windows.create_keystore.set(window)
        window.move_to_center(of=self._view)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_create_contact(self):
        self._create_contact()

    @pyqtSlot()
    @slot_exc_handler()
    @_require_keystore_selected
    def on_create_local_contact(self):
        selected_keystore_name = self._view.selected_keystore_name
        location = LocalWhitelistLocation(selected_keystore_name)
        self._create_contact(location)

    def _create_contact(self, location: Optional[ContactLocation] = None):
        window = CreateContactWindow(self._model.ctx, location)
        window.move_to_center(of=self._view)
        window.connect_created(self._on_contact_created)
        self._child_windows.create_contact.set(window)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_preferences(self):
        if self._model.background_task_service.busy:
            show_message_box_warning(title="Cannot open preferences",
                                     message="Tons is busy. Please wait before opening the preferences")
            return
        self._show_preferences()

    def _show_preferences(self):
        window = PreferencesWindow(self._model.ctx)
        window.move_to_center(of=self._view)
        self._child_windows.preferences.set(window)
        window.connect_configuration_changed(self._on_configuration_changed)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_transfer(self):
        self._transfer()

    @slot_exc_handler()
    def on_transfer_from(self, wallet: Union[WalletListItemData, bool] = False):
        wallet = wallet or self._view.selected_wallet_model
        self._transfer(wallet_from=wallet)

    @slot_exc_handler()
    def on_transfer_to(self, wallet: Union[WalletListItemData, bool] = False):
        wallet = wallet or self._view.selected_wallet_model
        self._transfer(wallet_to=wallet)

    @pyqtSlot()
    @slot_exc_handler()
    def on_open_transactions_history(self):
        self._open_transactions_history_window()

    def _open_transactions_history_window(self):
        window = TransactionsHistoryWindow(self._model.ctx, self._model.background_task_service)
        window.move_to_center(of=self._view)
        window.connect_edit_and_retry(self.on_edit_and_retry_transaction)
        window.connect_cancel(self._model.background_task_service.on_cancel_broadcast_task)
        self._child_windows.transactions_history.set(window)
        window.show()

    @_require_keystore_selected
    def _transfer(self,
                  wallet_from: Optional[WalletListItemData] = None,
                  wallet_to: Optional[WalletListItemData] = None):
        selected_keystore = self._model.keystore
        window = TransferWindow(self._model.ctx, selected_keystore, wallet_from, wallet_to)
        window.move_to_center(of=self._view)
        window.connect_transfer(self._model.background_task_service.on_transfer_task)
        window.connect_contact_created(self._on_contact_created)
        self._child_windows.transfer.set(window)
        window.show()

    @pyqtSlot()
    @slot_exc_handler()
    def on_init_wallet(self):
        wallet = self._view.selected_wallet_model
        record = wallet.entity
        assert isinstance(record, Record)

        try:
            with self.keystore_sensitive(self._model.keystore,
                                         f'Enter keystore password',
                                         f"Init {wallet.name} wallet"):
                self._model.init_wallet(record)
        except KeystoreNotUnlocked:
            return

    @pyqtSlot()
    @slot_exc_handler()
    def on_show_in_scanner(self):
        wallet = self._view.selected_wallet_model
        address = wallet.address
        show_in_scanner(address, self._model.network_is_testnet, self._model.scanner)

    @pyqtSlot()
    @slot_exc_handler()
    def on_export_wallet(self):
        wallet = self._view.selected_wallet_model
        record = wallet.entity
        assert isinstance(record, Record)

        try:
            with self.keystore_sensitive(self._model.keystore,
                                         f'Enter keystore password',
                                         f"Export {wallet.name}"):
                self._export_to_addr_and_pk(record)
        except KeystoreNotUnlocked:
            return

    @pyqtSlot(EditAndRetryInfo)
    @slot_exc_handler()
    def on_edit_and_retry_transaction(self, edit_and_retry_info: EditAndRetryInfo):
        if isinstance(edit_and_retry_info, TransferEditAndRetryInfo):
            return self._edit_and_retry_transfer(edit_and_retry_info)
        raise ValueError(f"Unknown EditAndRetryInfo kind: {type(edit_and_retry_info)}")

    def _edit_and_retry_transfer(self, edit_and_retry_info: TransferEditAndRetryInfo):
        keystore = self._model.get_keystore(edit_and_retry_info.keystore_name)

        wallet_from = None
        try:
            record = keystore.get_record_by_address(edit_and_retry_info.src, raise_none=True)
            wallet_from = WalletListItemData.from_record(record)
        except RecordDoesNotExistError:
            pass

        wallet_to = None
        recipient = get_recipient_by_address(keystore, self._model.ctx.whitelist, edit_and_retry_info.dst)
        if recipient is not None:
            if recipient.kind == RecipientKind.record:
                wallet_to = WalletListItemData.from_record(recipient.entity)
            elif recipient.kind == RecipientKind.local_contact:
                wallet_to = WalletListItemData.from_whitelist_contact(recipient.entity,
                                                                      WalletListItemKind.local_contact)
            elif recipient.kind == RecipientKind.global_contact:
                wallet_to = WalletListItemData.from_whitelist_contact(recipient.entity,
                                                                      WalletListItemKind.global_contact)
            else:
                raise NotImplementedError('unknown recipient kind: {recipient.kind}')

        preselected_info = TransferPreSelectedInfo(
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            amount=edit_and_retry_info.amount,
            comment=edit_and_retry_info.comment,
            encrypt_comment=edit_and_retry_info.encrypt_comment,
            state_init_path=edit_and_retry_info.state_init_path,
            body_path=edit_and_retry_info.body_path,
            transfer_all_coins=edit_and_retry_info.transfer_all_coins,
            destroy_if_zero=edit_and_retry_info.destroy_if_zero
        )

        window = TransferWindow.with_preselected_info(self._model.ctx, keystore, preselected_info)
        window.move_to_center(of=self._view)
        window.connect_transfer(self._model.background_task_service.on_transfer_task)
        window.connect_contact_created(self._on_contact_created)
        self._child_windows.transfer.set(window)
        window.show()

    @slot_exc_handler()
    def _export_to_addr_and_pk(self, record: Record):
        directory = QFileDialog.getExistingDirectory(parent=self._view,
                                                     caption='Select a directory to export wallet',
                                                     directory=_default_file_save_directory()
                                                     )
        if not directory:
            return
        self._model.export_to_addr_and_pk(record, directory)

    @pyqtSlot()
    @slot_exc_handler()
    def on_fetch_keystores_balance(self):
        self._model.invalidate_keystore_balance_info()

    @pyqtSlot()
    @slot_exc_handler()
    def on_copy_selected_wallet_address(self):
        selected_wallet = self._view.selected_wallet_model
        copy_to_clipboard(selected_wallet.address)

    @pyqtSlot(WalletMoveToLocation)
    @slot_exc_handler()
    def on_move_to(self, location: WalletMoveToLocation):
        self.__move_selected_wallet_to(location)

    def __move_selected_wallet_to(self, location: WalletMoveToLocation):
        selected_wallet = self._view.selected_wallet_model

        if selected_wallet.kind == WalletListItemKind.record:
            self._move_record(selected_wallet.entity, location.name)

        elif selected_wallet.kind in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:

            if selected_wallet.kind == WalletListItemKind.global_contact:
                old_location = GlobalWhitelistLocation()
            else:
                old_location = LocalWhitelistLocation(self._model.keystore.short_name)

            if location.kind == WalletMoveToLocationKind.global_whitelist:
                new_location = GlobalWhitelistLocation()
            elif location.kind == WalletMoveToLocationKind.local_whitelist:
                new_location = LocalWhitelistLocation(location.name)
            else:
                raise NotImplementedError

            self._move_contact(selected_wallet.entity, old_location, new_location)

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_backup_keystore(self, keystore_name: str):
        backup_path, _ = QFileDialog.getSaveFileName(self._view,
                                                     'Backup keystore',
                                                     os.path.join(
                                                         _default_file_save_directory(),
                                                         keystore_name + settings.KEYSTORE_FILE_EXT
                                                     ),
                                                     _BACKUP_MIME_FILTER,
                                                     _BACKUP_MIME_FILTER
                                                     )

        if not backup_path:
            return

        try:
            self._model.backup_keystore(keystore_name, backup_path)
        except FileNotFoundError as exception:
            show_message_box_warning('Failed to backup',
                                     f'No such file or directory: {exception.filename}')
        except Exception as exception:
            tons_logger().error(f'Failed to backup {keystore_name}', exc_info=exception)
            show_message_box_critical('Unexpected error', f'Failed to backup {keystore_name}')
        else:
            self._system_notify.emit(
                SystemNotification(
                    title=f'Keystore backup complete',
                    message=f'Saved to {backup_path}',
                    good=True
                )
            )

    @pyqtSlot(str)
    @slot_exc_handler()
    def on_export_keystore(self, keystore_name: str):
        export_path, _ = QFileDialog.getSaveFileName(self._view,
                                                     'Export keystore',
                                                     os.path.join(
                                                         _default_file_save_directory(),
                                                         keystore_name + '.json'
                                                     ),
                                                     _EXPORT_MIME_FILTER,
                                                     _EXPORT_MIME_FILTER
                                                     )
        if not export_path:
            return

        if not self._view.confirm_export_keystore(keystore_name):
            return

        keystore = self._model.get_keystore(keystore_name)

        try:
            with self.keystore_sensitive(keystore, 'Enter keystore password', f'Export {keystore_name}'):
                self._model.export_keystore(keystore, export_path)
        except KeystoreNotUnlocked:
            return
        except FileNotFoundError as exception:
            show_message_box_warning('Failed to export',
                                     f'No such file or directory: {exception.filename}')
        except Exception as exception:
            tons_logger().error(f'Failed to export {keystore_name}', exc_info=exception)
            show_message_box_critical('Unexpected error', f'Failed to export {keystore_name}')
        else:
            self._system_notify.emit(
                SystemNotification(
                    title=f'Keystore export complete',
                    message=f'Saved to {export_path}',
                    good=True
                )
            )

    @pyqtSlot()
    @slot_exc_handler()
    def on_import_keystore(self):
        backup_file_path, _ = QFileDialog.getOpenFileName(self._view,
                                                          "Import keystore",
                                                          _default_file_save_directory(),
                                                          _IMPORT_KEYSTORE_MIME_FILTER + ';;' + _ALL_MIME_FILTER,
                                                          _BACKUP_MIME_FILTER
                                                          )
        if not backup_file_path:
            return

        _, ext = os.path.splitext(backup_file_path)
        try:
            if ext.lower() == _KEYSTORE_EXT:
                self._import_encrypted_keystore(backup_file_path)
            elif ext.lower() == _EXPORTED_KEYSTORE_EXT:
                self._import_unencrypted_keystore(backup_file_path)
            else:
                try:
                    self._import_unknown_extension_keystore(backup_file_path)
                except _UnknownKeystoreFileContent:
                    show_message_box_warning('Unknown file content',
                                         f'Unknown file content inside the file: {backup_file_path}')
        except (InvalidKeyStoreError, InvalidBackupError, UnicodeDecodeError, JSONDecodeError):
            show_message_box_warning('Broken keystore backup',
                                     f'Unable to import the keystore from {backup_file_path}')

    def _import_encrypted_keystore(self, backup_file_path: str):
        keystore = self._model.get_keystore_from_path(backup_file_path)

        try:
            with self.keystore_sensitive(keystore,
                                         'Enter keystore password',
                                         'Import keystore'):
                keystore_backup = self._model.get_backup_from_encrypted(keystore)
                self._import_keystore(keystore_backup, backup_file_path)
        except KeystoreNotUnlocked:
            pass

    def _import_unencrypted_keystore(self, backup_file_path: str):
        keystore_backup = self._model.get_backup_from_unencrypted(backup_path=backup_file_path)
        self._import_keystore(keystore_backup, backup_file_path)

    def _import_unknown_extension_keystore(self, backup_file_path: str):
        try:
            self._import_encrypted_keystore(backup_file_path)
        except (InvalidKeyStoreError, UnicodeDecodeError, JSONDecodeError):
            try:
                self._import_unencrypted_keystore(backup_file_path)
            except (InvalidBackupError, InvalidKeyStoreError, UnicodeDecodeError, JSONDecodeError) as _exc:
                raise _UnknownKeystoreFileContent

    def _import_keystore(self, keystore_backup: KeystoreBackup, backup_file_path: str):
        window = ImportKeystoreWindow(self._model.ctx, keystore_backup, backup_file_path)
        self._child_windows.import_keystore_backup.set(window)
        window.move_to_center(of=self._view)
        window.connect_created(self._on_keystore_created)
        window.show()

    def _move_record(self, record: Record, new_keystore: str):
        if self._model.keystore.short_name == new_keystore:
            return

        keystore_src = self._model.keystore
        keystore_dst = self._model.get_keystore(new_keystore)

        try:
            with self.keystore_sensitive(keystore_src,
                                         'Enter keystore password',
                                         f"Move {record.name} wallet"):
                self.__move_record(record, keystore_src, keystore_dst)
        except KeystoreNotUnlocked:
            return

    def __move_record(self, record: Record, keystore_src: BaseKeyStore, keystore_dst: BaseKeyStore):
        try:
            self._model.move_record(record, keystore_src, keystore_dst)
        except RecordWithNameAlreadyExistsError:
            self._view.notify_record_with_name_already_exists(record.name, keystore_dst.short_name)
        except RecordWithAddressAlreadyExistsError as exception:
            self._view.notify_record_with_address_already_exists(exception.name, keystore_dst.short_name)
        except RecordNameInvalidError:
            self._view.notify_record_move_empty()
        else:
            self._on_keystore_modified(keystore_src.short_name)
            self._on_keystore_modified(keystore_dst.short_name)

    def _move_contact(self, contact: WhitelistContact, old_location: ContactLocation, new_location: ContactLocation):
        if old_location == new_location:
            return
        try:
            self._model.move_contact(contact, old_location, new_location)
        except WhitelistContactNameAlreadyExistsError:
            self._view.notify_contact_with_name_already_exists(contact.name, new_location)
        except WhitelistContactAddressAlreadyExistsError as exception:
            self._view.notify_contact_with_address_already_exists(exception.name, new_location)
        except WhitelistContactNameInvalidError:
            self._view.notify_contact_move_empty()
        except Exception as exception:
            self.on_notify_error(ErrorNotification(exception=exception, critical=True))
        else:
            self._on_contact_edited(old_location, new_location)

    @pyqtSlot(ErrorNotification)
    @slot_exc_handler()
    def on_notify_error(self, error_notification: ErrorNotification):
        if error_notification.critical:
            show_message_box_ = show_message_box_critical
        else:
            show_message_box_ = show_message_box_warning

        show_message_box_(error_notification.title, error_notification.message)

    @pyqtSlot(SystemNotification)
    @slot_exc_handler()
    def on_system_notification(self, notification: SystemNotification):
        if not notification.reset:
            notification.show()
            status_bar_message = StatusBarMessageModel(
                message=f'{notification.title} - {notification.message}',
                good=notification.good
            )
            self._view.status_bar.display(status_bar_message)
        else:
            self._view.status_bar.display(StatusBarMessageModel(message='', good=None))

    @pyqtSlot(WalletListItemData)
    @slot_exc_handler()
    def on_show_wallet_context_menu(self, wallet: WalletListItemData):
        model = WalletContextMenuModel.init(wallet,
                                            self._model.keystores_models,
                                            self._view.selected_sidebar_item)
        self._wallet_context_menu.display_model(model)
        self._wallet_context_menu.exec(self._view.mouse_position)

    @pyqtSlot(DnsListItemData)
    @slot_exc_handler()
    def on_show_dns_context_menu(self, dns: DnsListItemData):
        model = DnsContextMenuModel.from_dns_data(dns)
        self._dns_context_menu.display_model(model)
        self._dns_context_menu.exec(self._view.mouse_position)

    @pyqtSlot()
    @slot_exc_handler()
    def on_delete_wallet(self):
        wallet = self._view.selected_wallet_model
        assert self._view.selected_wallet_model is not None

        if not self._view.confirm_delete_wallet(wallet):
            return

        try:
            self._model.delete_wallet(wallet)
        except Exception as exception:
            tons_logger().critical(f'{type(exception).__name__}', exc_info=exception)
            show_message_box_critical(title='Unexpected error',
                                      message=f'{type(exception).__name__}')
            return

        self._on_wallet_deleted(wallet)

    def _on_wallet_deleted(self, wallet: WalletListItemData):
        if self._view.selected_keystore_name is not None:
            if wallet.kind in [WalletListItemKind.record, WalletListItemKind.local_contact]:
                self._on_keystore_modified(self._view.selected_keystore_name)

        if wallet.kind == WalletListItemKind.global_contact:
            self._on_global_whitelist_modified()

        for child_window in self._child_windows.all_windows():
            window = child_window.get()
            if isinstance(window, DeleteWalletSensitiveWindow):
                window.notify_wallet_deleted(wallet, self._view.selected_keystore_name)

    @slot_exc_handler()
    def _on_keystore_modified(self, keystore_name: str):
        self._model.invalidate_keystore_balance_info(keystore_name)
        if keystore_name == self._view.selected_keystore_name:
            self._model.update_keystore()
            self._display_wallets()
            self._display_dns()

    @slot_exc_handler()
    def _on_global_whitelist_modified(self):
        self._model.update_global_whitelist()
        self._display_wallets()
        self._display_keystores()
        self._display_whitelists()

    @slot_exc_handler()
    def _on_keystore_created(self):
        self._model.update_keystores()
        self._display_keystores()

    @slot_exc_handler()
    def _on_contact_created(self, location: ContactLocation):
        self._on_whitelist_modified(location)

    @pyqtSlot(ContactLocation, ContactLocation)
    @slot_exc_handler()
    def _on_contact_edited(self, old_location: ContactLocation, new_location: ContactLocation):
        self._on_whitelist_modified(old_location)
        self._on_whitelist_modified(new_location)

    def _on_whitelist_modified(self, location: ContactLocation):
        if isinstance(location, GlobalWhitelistLocation):
            self._on_global_whitelist_modified()
        elif isinstance(location, LocalWhitelistLocation):
            self._on_keystore_modified(location.keystore_name)
        else:
            raise NotImplementedError

    @pyqtSlot(ChangedFields)
    @slot_exc_handler()
    def _on_configuration_changed(self, changed_fields: ChangedFields):
        for window in self._child_windows.all_windows():
            window.close()

        if changed_fields.user_directory:
            self._view.set_zero_values()
            self._model.update_keystores()

        self._model.reinit_shared_object(self)
        keystore_name = self._view.selected_keystore_name
        self._model.init_list_wallets(keystore_name)
        self._dns_refresh_intent.connect(self._model.background_task_service.on_dns_tasks)
        self._display_model()
        self._model.invalidate_keystore_balance_info(clear=True)

    def _show_keystores_upgrade_info(self, keystores: List[BaseKeyStore]):
        # TODO refactor the upgrade (deeper)
        for keystore in keystores:
            upgrade_info = keystore.upgrade_info
            if upgrade_info.has_been_upgraded:
                title = f'Keystore {keystore.short_name} has been automatically upgraded.'
                message = f'Backup saved to: \n{os.path.relpath(upgrade_info.backup_path)}'
                show_system_notification(title, message)

    @pyqtSlot()
    @slot_exc_handler()
    def on_closed(self):
        self._model.stop_services()
        QApplication.quit()


    @property
    def _keystore_is_selected(self) -> bool:
        if self._view.selected_keystore_name is None:
            return False
        try:
            _ = self._model.keystore
        except (AttributeError, KeyStoreNotSelected):
            return False
        else:
            return True

    def handle_zero_state(self):
        dapp = self._model.ctx.config.provider.dapp
        if not any([dapp.api_key, dapp.testnet_api_key]):
            self._show_preferences()

    def _display_refresh_dns_menu(self):
        self._view.display_refresh_dns_menu(RefreshDnsMenuModel(self._model.ctx.config))

    def on_keystore_balances_changed(self):
        self._view.notify_keystores_updated()
