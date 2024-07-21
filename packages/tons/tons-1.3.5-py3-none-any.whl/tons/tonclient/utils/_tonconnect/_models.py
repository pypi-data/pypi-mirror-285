import time
from datetime import datetime

from pydantic import BaseModel, Field

from tons.tonsdk.utils.tonconnect.requests_responses import AppManifest


class TonconnectConnection(BaseModel):
    encrypted_priv_key: str
    dapp_client_id: str
    last_bridge_event_id: int
    last_wallet_event_id: int
    last_rpc_event_id: int
    wallet_name: str
    app_manifest: AppManifest
    connected_at: float = Field(default_factory=time.time)

    @property
    def connected_datetime(self):
        return datetime.fromtimestamp(self.connected_at)

    @property
    def next_event_id(self):
        return self.last_bridge_event_id + 1

    @property
    def next_rpc_event_id(self):
        return self.last_rpc_event_id + 1

    @property
    def next_wallet_event_id(self):
        return self.last_wallet_event_id + 1
