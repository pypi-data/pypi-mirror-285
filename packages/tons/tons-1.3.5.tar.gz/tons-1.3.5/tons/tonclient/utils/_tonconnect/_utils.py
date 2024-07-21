from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel

from tons.config import TonNetworkEnum
from tons.tonsdk.utils.tonconnect.requests_responses import TransactionPayload, TonconnectNetworkEnum


class SupportedTonconnectVersionEnum(str, Enum):
    v2 = "2"


class UniversalLink(BaseModel):
    v: SupportedTonconnectVersionEnum
    id: str
    r: str
    ref: Optional[str]

    class Config:
        use_enum_values = True


def get_network(param: Union[TransactionPayload]) -> TonNetworkEnum:
    if param.network == TonconnectNetworkEnum.mainnet:
        return TonNetworkEnum.mainnet
    elif param.network == TonconnectNetworkEnum.testnet:
        return TonNetworkEnum.testnet
    else:
        raise ValueError(f"Network {param.network} is not supported.")
