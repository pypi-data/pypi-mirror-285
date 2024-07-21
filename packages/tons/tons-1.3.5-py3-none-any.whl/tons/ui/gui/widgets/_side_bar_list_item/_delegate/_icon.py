from functools import lru_cache

from PyQt6.QtCore import QSize

from tons.ui.gui.utils import get_icon, get_icon_pixmap_size
from .._item_model import SideBarListItemKind


@lru_cache(maxsize=4)
def get_sidebar_icon_name(kind: SideBarListItemKind) -> str:
    matrix = {
        SideBarListItemKind.password_keystore: 'lock-solid.svg',
        SideBarListItemKind.global_whitelist: 'contact-global.svg',
    }
    return matrix[kind]


@lru_cache(maxsize=4)
def get_sidebar_icon_size(kind: SideBarListItemKind) -> QSize:
    icon_name = get_sidebar_icon_name(kind)
    return get_icon_pixmap_size(icon_name)
