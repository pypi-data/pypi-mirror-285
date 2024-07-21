import decimal

from pydantic import BaseModel, Field


class JettonConfig(BaseModel):
    gas_amount: decimal.Decimal = Field(default=decimal.Decimal('0.05'), ge=0)

    class Config:
        validate_assignment = True
