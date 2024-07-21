from copy import deepcopy
from typing import Optional, Dict

from ._bit_string import BitString
from ._cell import Cell
from ._message_relaxed import CommonMessageInfoRelaxed, MessageRelaxed, CommonMessageInfoRelaxedInternal


class Builder:
    def __init__(self):
        self.bits = BitString(1023)
        self.refs = []
        self.is_exotic = False

    def __repr__(self):
        return "<Builder refs_num: %d, %s>" % (len(self.refs), repr(self.bits))

    def store_cell(self, src: Cell):
        self.bits.write_bit_string(src.bits)
        self.refs += src.refs
        return self

    def store_ref(self, src: Cell):
        self.refs.append(src)
        return self

    def store_slice(self, src: 'Slice'):
        s = deepcopy(src)
        if s.remaining_bits > 0:
            self.store_bit_string(s.read_bits(s.remaining_bits))
        for _ in range(s.remaining_refs):
            self.store_ref(s.read_ref())

        return self

    def store_maybe_ref(self, src: Optional[Cell]):
        if src is not None:
            if not isinstance(src, Cell):
                raise ValueError("Maybe should be either Cell or None")
            self.bits.write_bit(1)
            self.store_ref(src)
        else:
            self.bits.write_bit(0)

        return self

    def store_bit(self, value):
        self.bits.write_bit(value)
        return self

    def store_bit_array(self, value):
        self.bits.write_bit_array(value)
        return self

    def store_uint(self, value, bit_length):
        self.bits.write_uint(value, bit_length)
        return self

    def store_uint8(self, value):
        self.bits.write_uint8(value)
        return self

    def store_int(self, value, bit_length):
        self.bits.write_int(value, bit_length)
        return self

    def store_string(self, value):
        self.bits.write_string(value)
        return self

    def store_bytes(self, value):
        self.bits.write_bytes(value)
        return self

    def store_bit_string(self, value):
        self.bits.write_bit_string(value)
        return self

    def store_address(self, value):
        self.bits.write_address(value)
        return self

    def store_grams(self, value):
        self.bits.write_grams(value)
        return self

    def store_coins(self, value):
        self.bits.write_coins(value)
        return self

    def store_currency_collection(self, coins: int, other: Optional[Dict[int, int]] = None):
        self.store_coins(coins)
        if other:
            raise NotImplementedError
        self.store_bit(0)
        return self

    def store_common_message_info_relaxed(self, source: CommonMessageInfoRelaxed) -> 'Builder':
        if not isinstance(source, CommonMessageInfoRelaxedInternal):
            raise NotImplementedError

        self.store_bit(0)
        self.store_bit(source.ihr_disabled)
        self.store_bit(source.bounce)
        self.store_bit(source.bounced)
        self.store_address(source.src)
        self.store_address(source.dest)
        self.store_currency_collection(source.value.coins, source.value.other)
        self.store_coins(source.ihr_fee)
        self.store_coins(source.forward_fee)
        self.store_uint(source.created_lt, 64)
        self.store_uint(source.created_at, 32)
        return self

    def store_message_relaxed(self, message: MessageRelaxed, force_ref: bool = False) -> 'Builder':
        self.store_common_message_info_relaxed(message.info)

        if message.init:
            raise NotImplementedError
        else:
            self.store_bit(False)

        # store body
        need_ref = True

        if not force_ref:
            if self.bits.get_free_bits() - 1 >= message.body.bits.get_used_bits():
                if len(self.refs) + len(message.body.refs) <= 4:
                    if not message.body.is_exotic:
                        need_ref = False

        if need_ref:
            self.store_bit(True)
            self.store_ref(message.body)
        else:
            self.store_bit(False)
            self.store_cell(message.body)

        return self


    def end_cell(self):
        cell = Cell()
        cell.write_cell(self)
        return cell


def begin_cell():
    return Builder()
