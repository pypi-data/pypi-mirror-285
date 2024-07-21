import gc
import weakref
from decimal import Decimal
from typing import Tuple, Union, List, Optional, Protocol

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from tons.config import TonNetworkEnum, TonScannerEnum
from tons.logging_ import tons_logger
from tons.tonclient._client._base import AddressInfoResult
from tons.tonclient.utils import Record, BaseKeyStore, WhitelistContact, KeyStoreTypeEnum
from tons.tonclient.utils._exceptions import RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, \
    RecordNameInvalidError, InvalidMnemonicsError, RecordDoesNotExistError, WhitelistContactDoesNotExistError, \
    InvalidPrivateKeyError
from tons.tonclient.utils._keystores import KeystoreBackup, PasswordKeyStore
from tons.tonsdk.utils import Address
from tons.ui.gui.services import address_info_service, setup_tx_info_service
from tons.ui.gui.exceptions import GuiException
from tons.ui.gui.services import setup_fiat_price_service
from tons.ui.gui.services import dns_info_service
from tons.ui.gui.services.fiat_price_service import stop_fiat_price_service
from tons.ui.gui.services.keystore_balance_service import setup_keystore_balance_service, stop_keystore_balance_service, \
    keystore_balance_service, KeystoreBalanceNotFetched
from tons.ui.gui.utils import init_shared_object_gui, BackgroundTaskService, DeployWalletTask, \
    ExportWalletTask, ErrorNotification, ContactLocation, SystemNotification, \
    ActionsHistory, slot_exc_handler
from tons.ui.gui.widgets import SideBarListItemModel, SideBarListItemKind, WalletListItemData, WalletListItemKind
from tons.ui.gui.windows.components.whitelists import WhitelistsModelComponent
from tons.ui.gui.windows.mixins.list_dns import ListDnsModel
from tons.ui.gui.windows.mixins.list_wallets import ListWalletsModel
from tons.utils import storage
from tons.utils.versioning import tons_is_outdated


class Presenter(Protocol):
    def on_notify_error(self, error: ErrorNotification): ...

    def on_system_notification(self, notification: SystemNotification): ...

    def on_keystore_balances_changed(self): ...


class MainWindowModel(QObject, ListWalletsModel, ListDnsModel):
    # TODO move transfer task here
    _deploy_wallet = pyqtSignal(DeployWalletTask)
    _export_wallet = pyqtSignal(ExportWalletTask)
    _keystore_balances_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ctx = init_shared_object_gui()  # TODO inspect and make sure that the ctx is never located anywhere else
        self._actions_history = ActionsHistory()
        self._setup_services()
        self._background_task_service = self._init_background_task_service()
        self._keystores: List[SideBarListItemModel] = []
        self._keystore: Optional[BaseKeyStore] = None
        # self._init_keystores()  # IMPORTANT: do not initialize keystores in constructor
        # (otherwise we will not be able to notify the user of the errors and modified keystores)
        self.init_list_wallets(keystore_name=None)
        self._setup_signals()

        self.whitelists = WhitelistsModelComponent(self.ctx)

    def _setup_signals(self):
        self._setup_my_signals_to_background_task_service()
        self._setup_keystore_balance_service_signals()

    def _setup_keystore_balance_service_signals(self):
        keystore_balance_service().fetched.connect(self._on_keystore_balance_fetched)

    def _setup_my_signals_to_background_task_service(self):
        self._deploy_wallet.connect(self._background_task_service.on_deploy_task)
        self._export_wallet.connect(self._background_task_service.on_export_wallet)

    def setup_signals(self, presenter: Presenter):
        self._setup_background_task_service_signals(presenter)
        self.setup_wallet_info_signals(presenter)
        self.setup_dns_info_signals(presenter)
        self._keystore_balances_changed.connect(presenter.on_keystore_balances_changed)

    def _setup_background_task_service_signals(self, presenter: Presenter):
        # TODO refactor: do not connect presenter to background task service,
        #  instead make your own signals for presenter
        self._background_task_service.connect_error(presenter.on_notify_error)
        self._background_task_service.connect_system_notify(presenter.on_system_notification)

    @property
    def keystore(self) -> BaseKeyStore:
        if self._keystore is None:
            raise KeyStoreNotSelected()
        return self._keystore

    def _init_keystores(self):
        keystore_names = sorted(self.ctx.keystores.keystore_names, key=lambda x: x.lower())
        self._keystores.clear()
        for keystore_name in keystore_names:
            keystore = self.get_keystore(keystore_name)
            if keystore.type == KeyStoreTypeEnum.yubikey:
                continue  # TODO Yubikey support

            item_model = SideBarListItemModel(
                kind=SideBarListItemKind.password_keystore,
                name=keystore_name,
                balance=None,
                count=len(keystore.get_records(False))
            )
            self._keystores.append(item_model)

        self._update_balances()

    def load_and_upgrade_all_keystores(self) -> List[BaseKeyStore]:
        return self.ctx.keystores.load_all()

    def init_keystores(self):
        self._init_keystores()

    def invalidate_keystore_balance_info(self, keystore_name: Optional[str] = None, clear: bool = False):
        if clear:
            for keystore_model in self.keystores_models:
                keystore_model.balance = None
            keystore_balance_service().invalidate()
        elif keystore_name is None:
            keystore_balance_service().request_update_all()
        else:
            keystore_balance_service().request_update(keystore_name)

    def update_keystores(self):
        self._init_keystores()

    def _update_balances(self):
        for keystore in self.keystores_models:
            try:
                keystore.balance = keystore_balance_service().balance(keystore.name)
            except KeystoreBalanceNotFetched:
                pass
        self._keystore_balances_changed.emit()

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_keystore_balance_fetched(self, keystore_name: str):
        self._update_balances()

    def reinit_shared_object(self, presenter: Presenter):
        self._background_task_service.stop()
        self.ctx.ton_daemon.stop()

        old_ctx = weakref.ref(self.ctx)  # TODO check ctx members
        old_bts = weakref.ref(self._background_task_service)

        self.ctx = init_shared_object_gui()
        self._setup_services()
        self.whitelists.setup(self.ctx)
        self._reinit_background_task_service(presenter)
        gc.collect()

        self._check_object_has_no_refs(old_ctx, 'ctx')
        self._check_object_has_no_refs(old_bts, 'background task service')

    def _setup_services(self):
        setup_tx_info_service(self.ctx)
        setup_fiat_price_service(self.ctx)
        setup_keystore_balance_service(self.ctx)
        address_info_service.setup(self.ctx)
        dns_info_service.setup(self.ctx)

    def _check_object_has_no_refs(self, obj: weakref.ReferenceType, name: str):
        if obj() is not None:
            tons_logger().error(
                f"Reference to the old {name} is still stored somewhere, which might signify broken logic.")
            for idx, ref in enumerate(gc.get_referrers(obj())):
                tons_logger().error(f'{idx}. {ref}')

    def _reinit_background_task_service(self, presenter: Presenter):
        self._background_task_service = self._init_background_task_service()
        self._setup_my_signals_to_background_task_service()
        # TODO refactor: do not reconnect presenter, instead make your own signals connected to presenter
        self._setup_background_task_service_signals(presenter)
        self._setup_keystore_balance_service_signals()

    def _init_background_task_service(self) -> BackgroundTaskService:
        background_task_service = BackgroundTaskService(self.ctx, self._actions_history)
        background_task_service.start()
        return background_task_service

    @property
    def keystores_models(self) -> Tuple[SideBarListItemModel, ...]:
        return tuple(self._keystores)

    @property
    def global_whitelist_sidebar_model(self) -> SideBarListItemModel:
        count = len(self.ctx.whitelist.get_contacts(True))
        return SideBarListItemModel(
            kind=SideBarListItemKind.global_whitelist,
            name="Global",
            count=count
        )

    @property
    def keystore_names(self) -> List[str]:
        return self.ctx.keystores.keystore_names

    @property
    def user_has_no_keystores(self) -> bool:
        return len(self.keystore_names) == 0

    @property
    def background_task_service(self) -> BackgroundTaskService:
        return self._background_task_service

    @property
    def whitelist_names(self) -> Tuple[str, ...]:
        contacts = self.ctx.whitelist.get_contacts(sorted_contacts=self.ctx.config.tons.sort_whitelist)
        return tuple(c.name for c in contacts)

    @property
    def total_ton_balance(self) -> Optional[Decimal]:
        if self._keystore is None:
            return None
        records = self._keystore.get_records(False)
        total = Decimal('0.0')
        for record in records:
            address_info = self.address_info(record.address)
            if address_info is None:
                return None
            record_balance = address_info.balance
            total += record_balance
        return total

    def get_keystore_wallets_count(self) -> int:
        records = self._get_records()
        return len(records)

    def get_local_whitelist_count(self) -> int:
        contacts = self._get_local_contacts()
        return len(contacts)

    def get_global_whitelist_count(self) -> int:
        contacts = self._get_global_contacts()
        return len(contacts)

    def get_keystore(self, keystore_name: str) -> BaseKeyStore:
        """ Loads the keystore from the file and upgrades it """
        return self.ctx.keystores.get_keystore(keystore_name, raise_none=True)  # TODO display message when it upgrades?

    def get_keystore_from_path(self, keystore_path: str) -> BaseKeyStore:
        return self.ctx.keystores.get_keystore_from_path(keystore_path, upgrade=False)

    def get_backup_from_encrypted(self, unlocked_keystore: BaseKeyStore) -> KeystoreBackup:
        if unlocked_keystore.type != KeyStoreTypeEnum.password:
            raise NotImplementedError("Only password keystore supported")

        json = KeystoreBackup.backup_json(unlocked_keystore)
        keystore_backup = KeystoreBackup.restore_from_tons(json)
        return keystore_backup

    def get_backup_from_unencrypted(self, backup_path: str) -> KeystoreBackup:
        json = storage.read_json(backup_path)
        keystore_backup = KeystoreBackup.restore_from_tons(json)
        return keystore_backup

    def get_contact(self, contact_name: str) -> WhitelistContact:
        return self.ctx.whitelist.get_contact(contact_name, raise_none=True)

    def get_wallet_names(self) -> Tuple[str, ...]:
        records = self._get_records()
        names = tuple()
        if all(isinstance(x, Record) for x in records):
            names = tuple(record.name for record in records)
        return names

    def init_wallet(self, record: Record):
        secret = self._keystore.get_secret(record)
        task = DeployWalletTask(
            secret=secret,
            record=record
        )
        self._deploy_wallet.emit(task)

    def delete_wallet(self, wallet: WalletListItemData):
        if wallet.kind == WalletListItemKind.global_contact:
            self.ctx.whitelist.delete_contact(wallet.entity, save=True)
        elif wallet.kind == WalletListItemKind.local_contact:
            assert self._keystore is not None
            self._keystore.whitelist.delete_contact(wallet.entity, save=True)
        elif wallet.kind == WalletListItemKind.record:
            assert self._keystore is not None
            self._keystore.delete_record(wallet.name, save=True)
        else:
            raise NotImplementedError("Unknown wallet kind")

        if self._keystore:
            self.invalidate_keystore_balance_info(keystore_name=self._keystore.name)

    @property
    def network_is_testnet(self) -> bool:
        return self.ctx.config.provider.dapp.network == TonNetworkEnum.testnet

    @property
    def scanner(self) -> TonScannerEnum:
        return self.ctx.config.gui.scanner

    def export_to_addr_and_pk(self, record: Record, destination_dir: str):
        secret = self._keystore.get_secret(record)
        task = ExportWalletTask(
            record=record,
            destination_dir=destination_dir,
            secret=secret
        )
        self._export_wallet.emit(task)

    def move_contact(self, contact: WhitelistContact, old_location: ContactLocation, new_location: ContactLocation):
        whitelist_dst = self.whitelists.get_whitelist(new_location)
        whitelist_dst.add_contact(contact.name, contact.address, contact.default_message, save=True)
        whitelist_src = self.whitelists.get_whitelist(old_location)
        whitelist_src.delete_contact(contact, save=True)

    def move_record(self, record: Record, keystore_src: BaseKeyStore, keystore_dst: BaseKeyStore):
        secret = keystore_src.get_secret(record)
        try:
            keystore_dst.add_new_record_from_secret(record.name,
                                                    secret,
                                                    record.version,
                                                    record.workchain,
                                                    record.subwallet_id,
                                                    record.comment,
                                                    save=True,
                                                    allow_empty_name=False)
        except (RecordWithNameAlreadyExistsError, RecordWithAddressAlreadyExistsError, RecordNameInvalidError):
            raise
        except (InvalidMnemonicsError, InvalidPrivateKeyError):
            assert False, "Secrets are loaded from keystore and thus should not be incorrect"

        keystore_src.delete_record(record.name, save=True)

    def fetch_keystores_balance(self):
        keystore_balance_service().request_update_all()

    def backup_keystore(self, keystore_name: str, backup_path: str):
        keystore = self.ctx.keystores.get_keystore(keystore_name)
        self.ctx.keystores.backup_keystore(keystore, backup_path, True)

    def export_keystore(self, unlocked_keystore: BaseKeyStore, export_path: str):
        self.ctx.keystores.backup_keystore(unlocked_keystore, export_path, False)

    def ensure_directories_exist(self):
        for default_dir_path in [self.ctx.config.tons.workdir,
                                 self.ctx.config.tons.keystores_path]:
            storage.ensure_dir_exists(default_dir_path)

    def tons_is_outdated(self) -> bool:
        return tons_is_outdated()

    def stop_services(self):
        stop_fiat_price_service()
        stop_keystore_balance_service()
        address_info_service.stop()
        dns_info_service.stop()
        self._background_task_service.halt()


class KeyStoreNotSelected(GuiException):
    def __init__(self):
        super().__init__("Keystore not selected")
