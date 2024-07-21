from collections import defaultdict
from datetime import timedelta
from typing import Tuple, Protocol, List, Optional, Dict

from tons.config import TonNetworkEnum
from tons.tonclient.utils import Record, BaseKeyStore
from tons.ui._utils import SharedObject, dns_expire_soon_threshold
from tons.ui.gui.widgets import DnsListItemData
from tons.ui.gui.windows.mixins.dns_info_service import MultiDnsInfoServiceModel


class Presenter(Protocol):
    def on_address_info_changed(self): ...


class ListDnsModel(MultiDnsInfoServiceModel):
    ctx: SharedObject
    _keystore: Optional[BaseKeyStore]

    def get_all_dns(self) -> Tuple[bool, Dict[str, Dict[str, DnsListItemData]], int]:
        keystore_wallets = self._get_records()
        return self._get_dns_address_info(keystore_wallets)

    def _get_records(self) -> Tuple[Record]:
        if self._keystore is None:
            return tuple()
        sort_records = self.ctx.config.tons.sort_keystore
        records = self._keystore.get_records(sort_records)
        return records

    def _get_dns_address_info(self, wallets: Tuple[Record]):
        dns_dict: Dict[str, Dict[str, DnsListItemData]] = defaultdict(dict)
        any_none = False
        count = 0

        max_expiring_in = dns_expire_soon_threshold(self.ctx.config.dns.max_expiring_in)
        for wallet in wallets:
            wallet_addr_key = wallet.tep_standard_user_address
            dns_records_data = self.dns_records(wallet.address)
            if dns_records_data is not None:
                for data in dns_records_data:
                    count += 1
                    dns_dict[wallet_addr_key][data.dns_domain] = \
                        DnsListItemData.from_nft_info_result(wallet_name=wallet.name,
                                                             wallet_address=wallet.tep_standard_user_address,
                                                             nft_info=data,
                                                             max_expiring_in=max_expiring_in)
            else:
                any_none = True

        return not any_none, dns_dict, count

    def domain_web_page(self, domain: str) -> str:
        """ expected domain without .ton """
        if self.network_is_testnet:
            return f"https://dns.ton.org/?testnet=true#{domain}"
        else:
            return f"https://dns.ton.org/#{domain}"


__all__ = ['ListDnsModel']
