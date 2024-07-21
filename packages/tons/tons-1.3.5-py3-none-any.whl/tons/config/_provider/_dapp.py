from enum import Enum
from typing import Optional

from pydantic import BaseModel

from tons import settings


class TonNetworkEnum(str, Enum):
    mainnet = 'mainnet'
    testnet = 'testnet'


class DAppConfig(BaseModel):
    api_key: Optional[str] = None
    testnet_api_key: Optional[str] = None
    network: TonNetworkEnum = TonNetworkEnum.mainnet

    class Config:
        use_enum_values = True
        validate_assignment = True

    @property
    def graphql_url(self):
        if self.network == TonNetworkEnum.mainnet:
            return settings.DAPP_MAINNET_GRAPHQL_URL
        else:
            return settings.DAPP_TESTNET_GRAPHQL_URL

    @property
    def broadcast_url(self):
        if self.network == TonNetworkEnum.mainnet:
            return settings.DAPP_MAINNET_BROADCAST_URL
        else:
            return settings.DAPP_TESTNET_BROADCAST_URL

    @property
    def websocket_url(self):
        assert self.graphql_url.startswith('https://'), \
            f"graphql_url {self.graphql_url} is invalid, doesn't start with https://"

        return 'wss://' + self.graphql_url[8:]

    @property
    def dns_collection_address(self):
        if self.network == TonNetworkEnum.mainnet:
            return settings.DNS_MAINNET_COLLECTION_ADDRESS
        else:
            return settings.DNS_TESTNET_COLLECTION_ADDRESS

    def __getattribute__(self, name):
        if name == 'api_key':
            return self.__get_api_key()
        return object.__getattribute__(self, name)

    def __get_api_key(self):
        if self.network == TonNetworkEnum.testnet and self.testnet_api_key:
            return self.testnet_api_key
        return self.__dict__['api_key']
