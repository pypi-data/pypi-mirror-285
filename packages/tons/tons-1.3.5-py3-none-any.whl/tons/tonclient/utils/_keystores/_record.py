from typing import Union, Optional

from pydantic import BaseModel, validator

from tons.tonsdk.contract.wallet import WalletVersionEnum
from tons.tonsdk.utils import Address, InvalidAddressError


class Record(BaseModel):
    name: str
    address: Union[str, Address]
    version: WalletVersionEnum
    workchain: int
    subwallet_id: Optional[int]
    secret_key: str
    comment: Optional[str] = ""

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

    @validator('comment')
    def validate_comment(cls, v, values, **kwargs) -> str:
        if v is None:
            return ''
        return v

    @validator('address')
    def validate_address(cls, v, values, **kwargs) -> str:
        if isinstance(v, Address):
            return v.to_string(False, False, False)

        try:
            addr = Address(v)
            return addr.to_string(False, False, False)

        except InvalidAddressError as e:
            raise ValueError(e)

    @property
    def address_to_show(self) -> str:
        return Address(self.address).to_string(True, True, True)

    @property
    def tep_standard_user_address(self) -> str:
        return Address(self.address).tep_standard_user_address
