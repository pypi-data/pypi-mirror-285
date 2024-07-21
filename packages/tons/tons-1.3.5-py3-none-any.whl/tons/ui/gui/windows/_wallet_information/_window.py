from typing import Optional

from tons.tonclient._client._base import AddressInfoResult
from tons.tonclient.utils import BaseKeyStore, Record
from tons.ui._utils import SharedObject

from ._model import WalletInformationModel
from ._view import WalletInformationView
from ._presenter import WalletInformationPresenter

from .._base import NormalWindow, DeleteWalletSensitiveWindow
from ...widgets import WalletListItemData, WalletListItemKind


class WalletInformationWindow(NormalWindow, DeleteWalletSensitiveWindow):
    def __init__(self, ctx: SharedObject,
                 keystore: BaseKeyStore,
                 record: Record):
        super().__init__()
        self._model = WalletInformationModel(ctx.keystores, keystore, record)
        self._view = WalletInformationView()
        self._presenter = WalletInformationPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_edited(self, slot):
        self._presenter.edited.connect(slot)

    def notify_wallet_deleted(self, deleted_wallet: WalletListItemData, keystore_name: Optional[str]):
        if deleted_wallet.kind != WalletListItemKind.record:
            return
        deleted_record: Record = deleted_wallet.entity
        if deleted_record == self._model.record:
            self.close()
