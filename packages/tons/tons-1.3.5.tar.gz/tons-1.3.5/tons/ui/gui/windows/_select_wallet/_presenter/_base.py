from abc import abstractmethod

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from tons.ui.gui.utils import QABCMeta, slot_exc_handler, LocalWhitelistLocation, SingleChildWindowManager
from tons.ui.gui.windows._create_contact import CreateContactWindow
from tons.ui.gui.widgets import WalletListItemData, WalletListItemKind
from tons.ui.gui.windows._select_wallet._model import SelectWalletModel
from tons.ui.gui.windows._select_wallet._view import SelectWalletView
from tons.ui.gui.windows.mixins.list_wallets import ListWalletsPresenter


class SelectWalletPresenter(QObject, ListWalletsPresenter, metaclass=QABCMeta):
    wallet_selected = pyqtSignal(WalletListItemData)
    contact_created = pyqtSignal(LocalWhitelistLocation)

    def __init__(self, model: SelectWalletModel, view: SelectWalletView):
        super().__init__()
        self._model: SelectWalletModel = model
        self._view: SelectWalletView = view

        self._set_wallet_items()
        self._view.setup_signals(self)

        self.create_contact_manager = SingleChildWindowManager()

        self.init_list_wallets()

        self.display_keystore_info()

    @abstractmethod
    def _set_wallet_items(self):
        raise NotImplementedError

    def display_keystore_info(self):
        self._view.keystore_name = self._model.keystore_name
        self._view.wallet_count = f'{self._model.records_count} records'

    @pyqtSlot(WalletListItemData)
    @slot_exc_handler()
    def on_wallet_list_item_selected(self, wallet_list_item_model: WalletListItemData):
        self.wallet_selected.emit(wallet_list_item_model)

    @pyqtSlot()
    @slot_exc_handler()
    def on_create_new_contact(self):
        location = LocalWhitelistLocation(self._view.keystore_name)
        window = CreateContactWindow(self._model.ctx, location)
        window.move_to_center(of=self._view)
        window.on_top()
        window.connect_created(self._on_contact_created)
        self.create_contact_manager.set(window)
        window.show()

    @pyqtSlot(LocalWhitelistLocation)
    @slot_exc_handler()
    def _on_contact_created(self, location: LocalWhitelistLocation):
        self._model.update_keystore()
        self._set_wallet_items()
        self.contact_created.emit(location)

    @pyqtSlot()
    @slot_exc_handler()
    def on_closed(self):
        self.create_contact_manager.close()
