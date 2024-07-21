from enum import Enum

from pydantic import BaseModel


class TonconnectNetworkEnum(str, Enum):
    mainnet = '-239'
    testnet = '-3'


class AppRequestMethodEnum(str, Enum):
    send_transaction = 'sendTransaction'
    sign_data = 'signData'


class TonConnectItemEnum(str, Enum):
    ton_addr = 'ton_addr'
    ton_proof = 'ton_proof'


class BridgeMessage(BaseModel):
    from_: str
    message: str

    class Config:
        fields = {
            'from_': 'from'
        }
