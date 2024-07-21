from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from tons.tonclient.utils import BaseKeyStore
from tons.ui._utils import SharedObject
from ._model import TransferModel
from ._presenter import TransferPresenter
from .._base import NormalWindow, DeleteWalletSensitiveWindow
from ._view import TransferView
from ...utils import xstr
from ...widgets import WalletListItemData, WalletListItemKind


class TransferPreSelectedInfo(BaseModel):
    wallet_from: Optional[WalletListItemData] = None
    wallet_to: Optional[WalletListItemData] = None
    amount: Optional[Decimal] = None
    comment: Optional[str] = None
    encrypt_comment: Optional[bool] = None
    state_init_path: Optional[str] = None
    body_path: Optional[str] = None
    transfer_all_coins: Optional[bool] = None
    destroy_if_zero: Optional[bool] = None


class TransferWindow(NormalWindow, DeleteWalletSensitiveWindow):
    def __init__(self, ctx: SharedObject, keystore: BaseKeyStore,
                 wallet_from: Optional[WalletListItemData] = None,
                 wallet_to: Optional[WalletListItemData] = None):
        super().__init__()
        self._model: TransferModel = TransferModel(ctx, keystore)
        self._view: TransferView = TransferView()
        self._presenter = TransferPresenter(self._model, self._view)

        self.init_normal_window()
        self._set_pre_selected_wallets(wallet_from, wallet_to)

    @classmethod
    def with_preselected_info(cls, ctx: SharedObject, keystore: BaseKeyStore,
                              info: TransferPreSelectedInfo) -> 'TransferWindow':
        obj = cls(ctx, keystore)
        obj._set_pre_selected_info(info)
        return obj

    def _set_pre_selected_info(self, info: TransferPreSelectedInfo):
        self._set_pre_selected_wallets(info.wallet_from, info.wallet_to)
        self._view.amount = xstr(info.amount)
        self._view.message = xstr(info.comment)
        self._view.encrypt_message = info.encrypt_comment
        self._view.state_init_boc_path = info.state_init_path
        self._view.body_boc_path = info.body_path
        self._view.transfer_all_coins = info.transfer_all_coins
        self._view.destroy_if_zero = info.destroy_if_zero
        if _advanced_options_preselected(info):
            self._view.show_advanced_options()


    def _set_pre_selected_wallets(self,
                                  wallet_from: Optional[WalletListItemData] = None,
                                  wallet_to: Optional[WalletListItemData] = None):
        if wallet_from is not None:
            if wallet_from.kind != WalletListItemKind.record:
                raise ValueError("Cannot transfer from a whitelist contact")
            self._presenter.on_wallet_from_selected(wallet_from)
        if wallet_to is not None:
            self._presenter.on_wallet_to_selected(wallet_to)

    def connect_transfer(self, slot):
        self._presenter.transfer_intent.connect(slot)

    def connect_contact_created(self, slot):
        self._presenter.contact_created.connect(slot)

    def notify_wallet_deleted(self, deleted_wallet: WalletListItemData, keystore_name: Optional[str]):
        if keystore_name != self._model.keystore_name:
            return
        self._presenter.on_some_wallet_deleted(deleted_wallet)


def _advanced_options_preselected(info: TransferPreSelectedInfo) -> bool:
    return any([info.encrypt_comment, info.state_init_path, info.body_path, info.transfer_all_coins, info.destroy_if_zero])