import decimal

from pydantic import BaseModel, Field


class MultiSigConfig(BaseModel):
    multisig_deploy_amount: decimal.Decimal = Field(default=decimal.Decimal('0.05'), ge=0)
    order_deploy_amount: decimal.Decimal = Field(default=decimal.Decimal('0.05'), ge=0)
    order_approve_send_amount: decimal.Decimal = Field(default=decimal.Decimal('0.05'), ge=0)

    class Config:
        validate_assignment = True
