from enum import Enum, auto
from typing import List, Sequence, Optional

from pydantic import BaseModel

from tons.tonclient._client._base import AddressState
from tons.tonsdk.contract.wallet import WalletContract
from tons.ui.gui.widgets import WalletListItemData, WalletListItemKind, SideBarListItemModel, SideBarListItemKind


class WalletMoveToLocationKind(Enum):
    keystore = auto()
    local_whitelist = auto()
    global_whitelist = auto()


class WalletMoveToLocation(BaseModel):
    kind: WalletMoveToLocationKind
    name: str


class WalletContextMenuModel(BaseModel):
    action_init_enabled: bool = False
    action_transfer_from_enabled: bool = False
    action_to_addr_and_pk_enabled: bool = False
    move_to_locations: List[WalletMoveToLocation] = []
    disabled_location_idx: Optional[int] = None
    max_allowed_width: int = 150

    @classmethod
    def init(cls, wallet: WalletListItemData, keystores: Sequence[SideBarListItemModel],
             selected: SideBarListItemModel) -> 'WalletContextMenuModel':
        obj = cls()
        obj.update_actions_ability(wallet)
        obj.update_locations(wallet, keystores, selected)
        return obj

    def update_actions_ability(self, wallet: WalletListItemData):
        self.action_transfer_from_enabled = wallet.kind == WalletListItemKind.record
        self.action_to_addr_and_pk_enabled = wallet.kind == WalletListItemKind.record
        self.action_init_enabled = (wallet.kind == WalletListItemKind.record) and \
                                   (wallet.address_info is not None) and \
                                   (wallet.address_info.state == AddressState.uninit) and \
                                   (wallet.address_info.balance >= WalletContract.init_amount(wallet.entity.version))

    def update_locations(self, wallet: WalletListItemData,
                         keystores: Sequence[SideBarListItemModel],
                         selected_sidebar: SideBarListItemModel):
        if wallet.kind == WalletListItemKind.record:
            keystore_location_kind = WalletMoveToLocationKind.keystore
        else:
            keystore_location_kind = WalletMoveToLocationKind.local_whitelist

        self.move_to_locations.clear()
        for idx, keystore in enumerate(keystores):
            if keystore == selected_sidebar:
                self.disabled_location_idx = idx
            location = WalletMoveToLocation(kind=keystore_location_kind, name=keystore.name)
            self.move_to_locations.append(location)

        if wallet.kind in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:
            self.move_to_locations.append(
                WalletMoveToLocation(kind=WalletMoveToLocationKind.global_whitelist,
                                     name='Global whitelist')
            )

            if wallet.kind == WalletListItemKind.global_contact:
                self.disabled_location_idx = -1
