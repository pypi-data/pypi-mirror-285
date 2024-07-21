from typing import Optional

from pydantic import BaseModel

from tons.ui.gui.widgets import DnsListItemData


class DnsContextMenuModel(BaseModel):
    owned: Optional[bool] = None

    @classmethod
    def from_dns_data(cls, dns: DnsListItemData):
        return cls(owned=dns.is_owned)
