from datetime import datetime, timedelta
from enum import Enum, auto
from functools import lru_cache
from typing import Dict, Optional, Tuple

from PyQt6.QtGui import QColor
from pydantic import root_validator

from tons.tonclient._client._base import NftItemInfoResult
from .._base import AbstractListItemModel
from ...utils import html_text_colored


@lru_cache
def _expired_color() -> QColor:
    return QColor(0xED, 0x6A, 0x5F)


class DnsListItemKind(Enum):
    owned = auto()
    taken = auto()


class DnsListItemData(AbstractListItemModel):
    wallet_name: str
    wallet_address: str
    kind: DnsListItemKind
    domain: str
    dns_expires: Optional[int]
    dns_account_address: str
    dns_last_fill_up_time: int
    dns_expiring_verbal_and_digits: Tuple[str, str]
    nft_info: Optional[NftItemInfoResult] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_nft_info_result(cls, wallet_name: str, wallet_address: str, nft_info: NftItemInfoResult,
                             max_expiring_in: datetime) -> 'DnsListItemData':
        return cls(
            wallet_name=wallet_name,
            wallet_address=wallet_address,
            kind=cls._get_dns_kind(nft_info),
            domain=nft_info.dns_domain,
            dns_expires=nft_info.dns_expires,
            dns_account_address=nft_info.account.address,
            dns_last_fill_up_time=nft_info.dns_last_fill_up_time,
            dns_expiring_verbal_and_digits=cls._get_expiring_verbal_and_digits(nft_info, max_expiring_in),
            nft_info=nft_info
        )

    @classmethod
    def skeleton(cls) -> 'DnsListItemData':
        return cls(wallet_name=f"My flashy wallet",
                   wallet_address="ABCDEFGHIJKLMNOPQRStuVWXYZnowiknowmyabcs12345678",
                   kind=DnsListItemKind.owned,
                   domain="tonstonstons",
                   dns_account_address="ABCDEFGHIJKLMNOPQRStuVWXYZnowiknowmyabcs12345678",
                   dns_last_fill_up_time=0,
                   dns_expiring_verbal_and_digits=("years", "600")
        )

    def find(self, prompt: str) -> Dict[str, int]:
        search_result = dict()
        for var in {'wallet_address', 'wallet_name', 'domain'}:
            val = getattr(self, var)
            if not isinstance(val, str):
                continue

            case_sensitive = var == 'wallet_address'
            if case_sensitive:
                res = val.find(prompt)
            else:
                res = val.lower().find(prompt.lower())

            if res > -1:
                search_result[var] = res
        return search_result

    def set_dns_info(self, dns_item_data: 'DnsListItemData'):
        self.wallet_name = dns_item_data.wallet_name
        self.wallet_address = dns_item_data.wallet_address
        self.kind = dns_item_data.kind
        self.domain = dns_item_data.domain
        self.dns_expires = dns_item_data.dns_expires
        self.dns_account_address = dns_item_data.dns_account_address
        self.dns_last_fill_up_time = dns_item_data.dns_last_fill_up_time
        self.dns_expiring_verbal_and_digits = dns_item_data.dns_expiring_verbal_and_digits
        self.nft_info = dns_item_data.nft_info

    @classmethod
    def _get_dns_kind(cls, nft_info: NftItemInfoResult) -> DnsListItemKind:
        if nft_info.dns_auction is not None and nft_info.dns_auction.max_bid_address is not None:
            return DnsListItemKind.taken
        elif nft_info.owner_address is not None:
            return DnsListItemKind.owned

        raise ValueError("Invalid nft_info in dns_kind")

    @classmethod
    def _get_expiring_verbal_and_digits(cls, nft_info: NftItemInfoResult,
                                        max_expiring_in: datetime) -> Tuple[str, str]:
        return cls._get_expiring_verbal_and_digits_from_timedelta(
            datetime.utcfromtimestamp(int(nft_info.dns_expires)), max_expiring_in
        )

    @classmethod
    def _get_expiring_verbal_and_digits_from_timedelta(cls, dns_expires_in: datetime,
                                                       max_expiring_in: datetime) -> Tuple[str, str]:
        dt = dns_expires_in - datetime.now()
        if dt <= timedelta(0):
            name, digits = 'expired', ''
        elif dt < timedelta(days=1):
            hours = dt.seconds // 3600
            minutes = (dt.seconds % 3600) // 60
            name, digits = 'hours', '%02d:%02d' % (hours, minutes)
        else:
            name, digits = 'days', f'{dt.days}'

        return name, cls._colorize(dns_expires_in < max_expiring_in, digits)

    @classmethod
    def _colorize(cls, expired, text):
        if expired:
            return html_text_colored(text, _expired_color())

        return text

    @property
    def is_owned(self):
        return self.kind == DnsListItemKind.owned

    def __eq__(self, other: Optional['DnsListItemData']):
        """ Note: this comparison is keystore-agnostic (does not take keystore name into account) """
        if other is None:
            return False

        return self.kind == other.kind \
               and self.domain == other.domain \
               and self.dns_last_fill_up_time == other.dns_last_fill_up_time \
               and self.wallet_name == other.wallet_name \
               and self.wallet_address == other.wallet_address


def _pretty_activity(activity: Optional[datetime]) -> str:
    if activity is None:
        return '(n/a)'
    now = datetime.now()

    if activity.day == now.day:
        result = activity.strftime("%H:%M:%S")
    else:
        result = activity.strftime("%d %b %Y")

    return result


__all__ = ['DnsListItemData',
           'DnsListItemKind']
