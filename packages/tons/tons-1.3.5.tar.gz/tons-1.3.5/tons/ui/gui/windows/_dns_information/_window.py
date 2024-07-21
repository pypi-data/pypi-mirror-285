from typing import Optional, Callable, Any

from tons.tonclient.utils import BaseKeyStore, Record
from tons.ui._utils import SharedObject
from ._model import DnsInformationModel
from ._presenter import DnsInformationPresenter
from ._view import DnsInformationView
from .._base import NormalWindow, DeleteWalletSensitiveWindow, ShowWalletInformationIntent
from ...widgets import WalletListItemData, DnsListItemData, WalletListItemKind


class DnsInformationWindow(NormalWindow, DeleteWalletSensitiveWindow):
    def __init__(self, ctx: SharedObject,
                 dns_item: DnsListItemData,
                 keystore: BaseKeyStore,
                 record: Record):
        super().__init__()
        self._model: DnsInformationModel = DnsInformationModel(ctx, dns_item, keystore, record)
        self._view: DnsInformationView = DnsInformationView()
        self._presenter = DnsInformationPresenter(self._model, self._view)

        self.init_normal_window()

    def notify_wallet_deleted(self, deleted_wallet: WalletListItemData, keystore_name: Optional[str]):
        if deleted_wallet.kind != WalletListItemKind.record:
            return
        deleted_record: Record = deleted_wallet.entity
        if deleted_record == self._model.record:
            self.close()

    def connect_show_wallet_information(self, slot: Callable[[ShowWalletInformationIntent], Any]):
        self._presenter.show_wallet_information.connect(slot)
