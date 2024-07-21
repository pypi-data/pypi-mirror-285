from typing import Tuple, Protocol, List, Optional

from tons.tonclient.utils import Record, WhitelistContact, BaseKeyStore
from tons.ui._utils import SharedObject
from tons.ui.gui.utils import init_global_whitelist
from tons.ui.gui.widgets import WalletListItemData, WalletListItemKind
from tons.ui.gui.windows.mixins.wallet_info_service import MultiWalletInfoServiceModel


class Presenter(Protocol):
    def on_address_info_changed(self): ...


class ListWalletsModel(MultiWalletInfoServiceModel):
    ctx: SharedObject
    _keystore: Optional[BaseKeyStore]

    def init_list_wallets(self, keystore_name: Optional[str]):
        self.set_keystore(keystore_name)

    def set_keystore(self, keystore_name: Optional[str]):
        if keystore_name is None:
            keystore = None
        else:
            keystore = self.ctx.keystores.get_keystore(keystore_name)
        self._set_keystore(keystore)

    def _set_keystore(self, keystore: Optional[BaseKeyStore]):
        self._keystore = keystore

    def update_keystore(self):
        keystore_name = self._keystore.short_name
        self.set_keystore(keystore_name)

    def update_global_whitelist(self):
        self.ctx.whitelist = init_global_whitelist(self.ctx.config)

    def _get_records(self) -> Tuple[Record]:
        if self._keystore is None:
            return tuple()
        sort_records = self.ctx.config.tons.sort_keystore
        records = self._keystore.get_records(sort_records)
        return records

    def _get_local_contacts(self) -> Tuple[WhitelistContact]:
        if self._keystore is None:
            return tuple()
        sort_contacts = self.ctx.config.tons.sort_whitelist
        whitelist = self._keystore.whitelist
        local_contacts = whitelist.get_contacts(sort_contacts)
        return local_contacts

    def _get_global_contacts(self) -> Tuple[WhitelistContact]:
        sort_contacts = self.ctx.config.tons.sort_whitelist
        whitelist = self.ctx.whitelist
        global_contacts = whitelist.get_contacts(sort_contacts)
        return global_contacts

    def get_all_wallets(self) -> List[WalletListItemData]:
        wallets: List[WalletListItemData] = []

        wallets += self.get_wallets_records()
        wallets += self.get_wallets_local_whitelist()
        wallets += self.get_wallets_global_whitelist()

        self._set_existing_address_info(wallets)

        return wallets

    def get_wallets_records(self) -> List[WalletListItemData]:
        records = self._get_records()
        wallets = [WalletListItemData.from_record(record) for record in records]
        return wallets

    def get_wallets_local_whitelist(self) -> List[WalletListItemData]:
        local_contacts = self._get_local_contacts()
        wallets = [WalletListItemData.from_whitelist_contact(contact, WalletListItemKind.local_contact)
                   for contact in local_contacts]
        return wallets

    def get_wallets_global_whitelist(self) -> List[WalletListItemData]:
        global_contacts = self._get_global_contacts()
        wallets = [WalletListItemData.from_whitelist_contact(contact, WalletListItemKind.global_contact)
                   for contact in global_contacts]

        return wallets

    def _set_existing_address_info(self, wallets: List[WalletListItemData]):
        for wallet in wallets:
            address_info = self.address_info(wallet.address)
            if address_info is not None:
                wallet.set_address_info(address_info)


__all__ = ['ListWalletsModel']
