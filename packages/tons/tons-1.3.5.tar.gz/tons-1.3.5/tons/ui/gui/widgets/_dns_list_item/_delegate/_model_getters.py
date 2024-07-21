from typing import Tuple

from .._item_data import DnsListItemData


def get_dns_name(dns: DnsListItemData) -> str:
    return dns.domain


def get_expiring_verbal_and_digits(data: DnsListItemData) -> Tuple[str, str]:
    return data.dns_expiring_verbal_and_digits
