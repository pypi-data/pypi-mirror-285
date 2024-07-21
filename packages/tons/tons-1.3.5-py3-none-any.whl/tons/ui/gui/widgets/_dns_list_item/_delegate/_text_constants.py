from functools import lru_cache

from .._item_data import DnsListItemKind


@lru_cache
def dns_visual_noise() -> str:
    return "TON DNS Domains ✓"


@lru_cache
def filter_by_this_wallet() -> str:
    return "Filter by this wallet"


@lru_cache
def dot_ton() -> str:
    return '.ton'


_state_text_map = {DnsListItemKind.owned: 'Owned', DnsListItemKind.taken: 'Taken'}


def state_text(dns_item_kind: DnsListItemKind) -> str:
    return _state_text_map[dns_item_kind]