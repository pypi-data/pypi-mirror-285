from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from .._base import AbstractListItemModel


class SideBarListItemKind(Enum):
    password_keystore = auto()
    global_whitelist = auto()
    # yubikey_keystore = auto() # TODO


class SideBarListItemModel(AbstractListItemModel):
    kind: SideBarListItemKind
    name: str
    balance: Optional[Decimal]
    count: Optional[int]
    # disabled: bool  # TODO
