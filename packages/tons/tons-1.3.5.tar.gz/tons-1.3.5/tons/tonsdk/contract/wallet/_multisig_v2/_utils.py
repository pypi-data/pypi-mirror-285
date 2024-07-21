from typing import List, Optional, Dict, Any, Sequence

from tons.tonsdk.boc import Cell, begin_dict, begin_cell, Slice
from tons.tonsdk.boc.dict.deserialize_dict import parse_dict
from tons.tonsdk.contract.wallet._multisig_v2._constants import _BitSize
from tons.tonsdk.utils import Address


def addresses_to_cell(addresses: Sequence[Address]) -> Optional[Cell]:
    if len(addresses) == 0:
        return None
    d = begin_dict(_BitSize.SIGNER_INDEX)
    for i, addr in enumerate(addresses):
        c = begin_cell().store_address(addr).end_cell()
        d.store_cell(i, c)

    return d.end_cell()


def cell_to_addresses(cell: Optional[Cell]) -> Dict[int, Address]:
    if cell is None:
        return dict()
    def _extract_address(s: Slice) -> Address:
        return s.read_msg_addr()
    return parse_dict(cell.begin_parse(), _BitSize.SIGNER_INDEX, _extract_address)


def dict_to_list(d: Dict[int, Any]) -> List[Any]:
    assert sorted(d) == list(range(len(d)))
    return [d[idx] for idx in sorted(d)]
