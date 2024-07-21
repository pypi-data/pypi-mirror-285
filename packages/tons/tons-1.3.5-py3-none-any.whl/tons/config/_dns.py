import decimal

from pydantic import BaseModel, Field


class DnsConfig(BaseModel):
    max_expiring_in: int = Field(default=6, ge=1, le=12)
    refresh_send_amount: decimal.Decimal = Field(default=decimal.Decimal('0.006'), ge=0)
    refresh_not_yet_owned_send_amount: decimal.Decimal = Field(default=decimal.Decimal('0.015'), ge=0)

    class Config:
        validate_assignment = True
