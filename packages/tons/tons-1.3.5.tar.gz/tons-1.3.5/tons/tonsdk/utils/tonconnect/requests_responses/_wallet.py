import platform
from enum import Enum
from typing import Optional, List, Union, Literal, Any

from pydantic import BaseModel, validator

from tons.tonsdk.utils import Address, InvalidAddressError
from ._common import AppRequestMethodEnum, TonconnectNetworkEnum, TonConnectItemEnum


class ConnectEventErrorCodeEnum(int, Enum):
    unknown_error = 0
    bad_request = 1
    app_manifest_not_found = 2
    app_manifest_content_error = 3
    unknown_app = 100
    user_declined_the_connection = 300


class SendTransactionResponseErrorCodeEnum(int, Enum):
    unknown_error = 0
    bad_request = 1
    unknown_app = 100
    user_declined_the_connection = 300
    method_not_supported = 400


class ConnectItemErrorCodeEnum(int, Enum):
    unknown_error = 0
    method_is_not_supported = 400


class WalletEventNameEnum(str, Enum):
    connect = "connect"
    connect_error = "connect_error"
    disconnect = "disconnect"


class SendTransactionFeature(BaseModel):
    name: Literal[AppRequestMethodEnum.send_transaction] = AppRequestMethodEnum.send_transaction
    maxMessages: int

    class Config:
        use_enum_values = True


class SignDataFeature(BaseModel):
    name: Literal[AppRequestMethodEnum.sign_data] = AppRequestMethodEnum.sign_data

    class Config:
        use_enum_values = True


class DeviceInfo(BaseModel):
    platform: Literal["iphone", "ipad", "android", "windows", "mac", "linux"]
    appName: str
    appVersion: str
    maxProtocolVersion: int
    # todo: uncomment when tonconnect-sdk supports this feature
    # features: List[Union[SendTransactionFeature, SignDataFeature]]
    features: List[str] = ["SendTransaction"]

    @staticmethod
    def find_platform():
        platform_name = platform.system().lower()
        if platform_name == "linux":
            return "linux"
        elif platform_name == "darwin":
            return "mac"
        elif platform_name == "windows":
            return "windows"
        else:
            raise OSError("Device info unknown platform.")


class TonAddressItemReply(BaseModel):
    name: TonConnectItemEnum.ton_addr = TonConnectItemEnum.ton_addr
    address: str
    network: TonconnectNetworkEnum
    publicKey: str
    walletStateInit: str

    class Config:
        use_enum_values = True

    @validator('address')
    def validate_address(cls, v, values, **kwargs):
        try:
            addr = Address(v)
            return addr.to_string(False)

        except InvalidAddressError as e:
            raise ValueError(e)


class ConnectItemError(BaseModel):
    code: ConnectItemErrorCodeEnum
    message: Optional[str]


class ConnectItemReplyError(BaseModel):
    name: TonConnectItemEnum
    error: ConnectItemError

    class Config:
        use_enum_values = True


class ConnectEventSuccessPayload(BaseModel):
    items: List[Union[TonAddressItemReply, ConnectItemReplyError]]  # todo: implement ton proof
    device: DeviceInfo


class ConnectEventSuccess(BaseModel):
    event: Literal["connect"] = "connect"
    id: int
    payload: ConnectEventSuccessPayload


class ConnectEventErrorPayload(BaseModel):
    code: ConnectEventErrorCodeEnum
    message: str

    class Config:
        use_enum_values = True


class ConnectEventError(BaseModel):
    event: Literal["connect_error"] = "connect_error"
    id: int
    payload: ConnectEventErrorPayload


class DisconnectEvent(BaseModel):
    event: Literal["disconnect"] = "disconnect"
    id: int
    payload: dict = {}


class WalletResponseErrorPayload(BaseModel):
    code: int
    message: Optional[str]
    data: Optional[Any]


class WalletResponseError(BaseModel):
    error: WalletResponseErrorPayload
    id: str


class WalletResponseSuccess(BaseModel):
    result: str
    id: str


class WalletEvent(BaseModel):
    event: WalletEventNameEnum
    id: int
    payload: Union[ConnectEventSuccess, ConnectEventError]  # todo: implement disconnect

    class Config:
        use_enum_values = True
