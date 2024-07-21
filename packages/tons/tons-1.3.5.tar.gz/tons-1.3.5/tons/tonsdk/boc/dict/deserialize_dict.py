import math
from typing import Dict, Callable, Any, Optional

from tons.tonsdk.boc import Cell, Slice


def read_unary_length(s: Slice) -> int:
    res = 0
    while s.read_bit():
        res += 1
    return res


def do_parse(prefix: str, s: Slice, n: int, result: Dict[int, Any],
             extractor: Callable[[Slice], Any]):
    lb0 = s.read_bit()
    prefix_length = 0
    pp = prefix
    if not lb0:
        # short label detected
        prefix_length = read_unary_length(s)
        for _ in range(prefix_length):
            pp += '1' if s.read_bit() else '0'
    else:
        lb1 = s.read_bit()
        if not lb1:
            # long label detected
            prefix_length = s.read_uint(math.ceil(math.log2(n + 1)))
            for _ in range(prefix_length):
                pp += '1' if s.read_bit() else '0'
        else:
            # same label detected
            bit = '1' if s.read_bit() else '0'
            prefix_length = s.read_uint(math.ceil(math.log2(n + 1)))
            for _ in range(prefix_length):
                pp += bit

    if n - prefix_length == 0:
        key = int(pp, 2)
        result[key] = extractor(s)

    else:
        left: Cell = s.read_ref()
        right: Cell = s.read_ref()

        if not left.is_exotic:
            do_parse(pp + '0', left.begin_parse(), n - prefix_length - 1, result, extractor)
        if not right.is_exotic:
            do_parse(pp + '1', right.begin_parse(), n - prefix_length - 1, result, extractor)


def parse_dict(slice_: Slice, key_size: int, extractor: Callable[[Slice], Any]) -> Dict[int, Any]:
    result = dict()
    do_parse(prefix='', s=slice_, n=key_size, result=result, extractor=extractor)
    return result