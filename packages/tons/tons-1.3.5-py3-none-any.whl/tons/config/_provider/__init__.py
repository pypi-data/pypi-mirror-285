from pydantic import BaseModel, Field

from ._dapp import DAppConfig, TonNetworkEnum


class ProviderConfig(BaseModel):
    dapp: DAppConfig = Field(default_factory=DAppConfig)

    class Config:
        validate_assignment = True


__all__ = [
    "DAppConfig",
    "TonNetworkEnum",
    "ProviderConfig",
]
