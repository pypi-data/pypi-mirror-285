import dataclasses
from typing import Optional, Dict, Union

from ._cell import Cell
from tons.tonsdk.utils import Address


@dataclasses.dataclass
class CurrencyCollection:
    coins: int
    other: Union[None, Dict[int, int], Cell] = None # TODO parse


@dataclasses.dataclass
class CommonMessageInfoRelaxedInternal:
    ihr_disabled: bool
    bounce: bool
    bounced: bool
    src: Optional[Address]
    dest: Address
    value: CurrencyCollection
    ihr_fee: int
    forward_fee: int
    created_lt: int
    created_at: int


@dataclasses.dataclass
class CommonMessageInfoRelaxedExternalOut:
    ...
    # src: Optional[Address]
    # dest: Optional[Address] # ?? EXTERNAL ADDRESS


CommonMessageInfoRelaxed = Union[CommonMessageInfoRelaxedInternal, CommonMessageInfoRelaxedExternalOut]

@dataclasses.dataclass
class MessageRelaxed:
    info: Union[CommonMessageInfoRelaxedInternal, CommonMessageInfoRelaxedExternalOut]
    body: Cell
    init: Optional[Cell] = None