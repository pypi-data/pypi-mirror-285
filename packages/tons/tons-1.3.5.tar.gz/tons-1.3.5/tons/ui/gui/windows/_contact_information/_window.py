from typing import Optional

from tons.tonclient._client._base import AddressInfoResult
from tons.tonclient.utils import WhitelistContact
from tons.ui._utils import SharedObject

from ._model import ContactInformationModel
from ._view import ContactInformationView
from ._presenter import ContactInformationPresenter

from .._base import NormalWindow, DeleteWalletSensitiveWindow
from ...utils import ContactLocation, LocalWhitelistLocation, GlobalWhitelistLocation
from ...widgets import WalletListItemData, WalletListItemKind


class ContactInformationWindow(NormalWindow, DeleteWalletSensitiveWindow):
    def __init__(self, ctx: SharedObject,
                 contact: WhitelistContact,
                 location: ContactLocation):
        super().__init__()
        self._model = ContactInformationModel(ctx, contact, location)
        self._view = ContactInformationView()
        self._presenter = ContactInformationPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_edited(self, slot):
        self._presenter.edited.connect(slot)

    def notify_wallet_deleted(self, deleted_wallet: WalletListItemData, keystore_name: Optional[str]):
        if deleted_wallet.kind not in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:
            return

        if deleted_wallet.kind == WalletListItemKind.local_contact:
            if not isinstance(self._model.location, LocalWhitelistLocation):
                return
            if self._model.location.keystore_name != keystore_name:
                return

        if deleted_wallet.kind == WalletListItemKind.global_contact:
            if not isinstance(self._model.location, GlobalWhitelistLocation):
                return

        deleted_contact = deleted_wallet.entity

        if self._model.contact == deleted_contact:
            self.close()
