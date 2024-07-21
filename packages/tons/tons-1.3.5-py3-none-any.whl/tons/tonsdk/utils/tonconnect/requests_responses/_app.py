from typing import List, Literal, Union, Optional

from pydantic import BaseModel

from ._common import AppRequestMethodEnum, TonconnectNetworkEnum, TonConnectItemEnum


class AppRequest(BaseModel):
    method: AppRequestMethodEnum
    params: List[str]
    id: int

    class Config:
        use_enum_values = True


class TonAddressItem(BaseModel):
    name: Literal[TonConnectItemEnum.ton_addr]


class TonProofItem(BaseModel):
    name: Literal[TonConnectItemEnum.ton_proof]
    payload: str


class ConnectRequest(BaseModel):
    manifestUrl: str
    items: List[Union[TonAddressItem, TonProofItem]]


class AppManifest(BaseModel):
    url: str
    name: str
    iconUrl: str
    termsOfUseUrl: Optional[str]
    privacyPolicyUrl: Optional[str]


class MessagePayload(BaseModel):
    address: str
    amount: str
    payload: Optional[str]
    stateInit: Optional[str]

    def __str__(self):
        return f'Message(address={self.address}, amount={self.amount}, ' \
               f'payload={self.payload}, stateInit={self.stateInit})'


class TransactionPayload(BaseModel):
    valid_until: Optional[int]
    network: Optional[TonconnectNetworkEnum]
    from_: Optional[str]
    messages: List[MessagePayload]

    class Config:
        fields = {
            'from_': 'from'
        }

    def __str__(self):
        return f'TransactionPayload(valid_until={self.valid_until}, ' \
               f'network={self.network.name if self.network else None}, ' \
               f'from={self.from_}, messages={self.messages})'


class SendTransactionRequest(BaseModel):
    method: Literal[AppRequestMethodEnum.send_transaction]
    params: List[Union[TransactionPayload]]
    id: str
