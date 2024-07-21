from enum import Enum

from pydantic import BaseModel, Field


class TonScannerEnum(str, Enum):
    tonscan = 'tonscan.org'
    tonviewer = 'tonviewer.com'
    toncx = 'ton.cx'


class GuiConfig(BaseModel):
    scanner: TonScannerEnum = TonScannerEnum.tonscan

    class Config:
        use_enum_values = True
        validate_assignment = True