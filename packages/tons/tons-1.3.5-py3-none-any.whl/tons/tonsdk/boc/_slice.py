from copy import deepcopy
from typing import Optional

import bitarray

from ._message_relaxed import MessageRelaxed
from ._builder import begin_cell
from ._cell import Cell
from ._message_relaxed import CommonMessageInfoRelaxed, CurrencyCollection, CommonMessageInfoRelaxedInternal
from ..utils._address import Address


class Slice:
    """Slice like an analog of slice in FunC. Used only for reading."""

    def __init__(self, cell: Cell):
        self.bits = bitarray.bitarray()
        self.bits.frombytes(cell.bits.array)
        self.bits = self.bits[:cell.bits.cursor]
        self.refs = cell.refs
        self.ref_offset = 0

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return str(self.bits)

    def __repr__(self):
        return f"<Slice refs: {self.remaining_refs}, {repr(self.bits)}>"

    def is_empty(self) -> bool:
        return len(self.bits) == 0

    def end_parse(self):
        """Throws an exception if the slice is not empty."""
        if not self.is_empty() or self.ref_offset != len(self.refs):
            raise ValueError("Slice is not empty.")

    def read_bit(self) -> int:
        """Reads single bit from the slice."""
        bit = self.bits[0]
        del self.bits[0]
        return bit

    def preload_bit(self) -> int:
        return self.bits[0]

    def read_bits(self, bit_count: int) -> bitarray.bitarray:
        bits = self.bits[:bit_count]
        del self.bits[:bit_count]
        return bits

    def preload_bits(self, bit_count: int) -> bitarray.bitarray:
        return self.bits[:bit_count]

    def skip_bits(self, bit_count: int):
        del self.bits[:bit_count]

    def read_uint(self, bit_length: int) -> int:
        value = self.bits[:bit_length]
        del self.bits[:bit_length]
        return int(value.to01(), 2)

    def preload_uint(self, bit_length: int) -> int:
        value = self.bits[:bit_length]
        return int(value.to01(), 2)

    def read_bytes(self, bytes_count: int) -> bytes:
        length = bytes_count * 8
        value = self.bits[:length]
        del self.bits[:length]
        return value.tobytes()

    def read_int(self, bit_length: int) -> int:
        if bit_length == 1:
            # if num is -1 then bit is 1. if 0 then 1. see _bit_string.py
            return - self.read_bit()
        else:
            is_negative = self.read_bit()
            value = self.read_uint(bit_length - 1)
            if is_negative == 1:
                # ones complement
                return - (2 ** (bit_length - 1) - value)
            else:
                return value

    def read_common_message_info_relaxed(self) -> CommonMessageInfoRelaxed:
        if not self.read_bit(): # Internal message
            ihr_disabled = bool(self.read_bit())
            bounce = bool(self.read_bit())
            bounced = bool(self.read_bit())
            src = self.read_msg_addr()
            dest = self.read_msg_addr()
            value = self.read_currency_collection()
            ihr_fee = self.read_coins()
            forward_fee = self.read_coins()
            created_lt = self.read_uint(64)
            created_at = self.read_uint(32)

            return CommonMessageInfoRelaxedInternal(
                ihr_disabled=ihr_disabled,
                bounce=bounce,
                bounced=bounced,
                src=src,
                dest=dest,
                value=value,
                ihr_fee=ihr_fee,
                forward_fee=forward_fee,
                created_lt=created_lt,
                created_at=created_at
            )

        if not self.read_bit():
            raise ValueError("External In message is not possible for CommonMessageInfoRelaxed")

        # external out message
        # src = self.read_msg_addr()
        # dest = self.read_external_address()  # not implemented
        # created_lt = self.load_uint(64)
        # created_at = self.load_uint(32)

        raise NotImplementedError

    def read_message_relaxed(self) -> MessageRelaxed:
        info = self.read_common_message_info_relaxed()
        init = None
        state_init_present = self.read_bit()
        if state_init_present:
            raise NotImplementedError
        ref = self.read_bit()
        if ref:
            body = self.read_ref()
        else:
            body = self.as_cell()
        return MessageRelaxed(info=info, init=init, body=body)

    def read_currency_collection(self) -> CurrencyCollection:
        coins = self.read_coins()
        other = self.read_maybe_ref()  # TODO parse dict
        return CurrencyCollection(coins=coins,
                                  other=other)

    def read_maybe_ref(self) -> Optional[Cell]:
        present = self.read_bit()
        if not present:
            return None
        return self.read_ref()

    def preload_int(self, bit_length: int) -> int:
        tmp = deepcopy(self.bits)
        value = self.read_int(bit_length)
        self.bits = tmp
        return value

    def read_msg_addr(self) -> Optional[Address]:
        """Reads contract address from the slice.
        May return None if there is a zero-address."""
        if self.read_uint(2) == 0:
            return None
        self.read_bit()  # anycast
        workchain_id = hex(self.read_int(8)).replace('0x', '')
        hashpart = self.read_bytes(32).hex()
        return Address(workchain_id + ":" + hashpart)

    def read_coins(self) -> int:
        """Reads an amount of coins from the slice. Returns nanocoins."""
        length = self.read_uint(4)
        if length == 0:  # 0 in length means 0 coins
            return 0
        else:
            return self.read_uint(length * 8)

    def read_grams(self) -> int:
        """Reads an amount of coins from the slice. Returns nanocoins."""
        return self.read_coins()

    def read_string(self, length: int = 0) -> str:
        """Reads string from the slice.
        If length is 0, then reads string until the end of the slice."""
        if length == 0:
            length = len(self.bits) // 8
        return self.read_bytes(length).decode("utf-8")

    def read_ref(self) -> Cell:
        """Reads next reference cell from the slice."""
        ref = self.refs[self.ref_offset]
        self.ref_offset += 1
        return ref

    def preload_ref(self) -> Cell:
        return self.refs[self.ref_offset]

    def load_dict(self) -> Optional[Cell]:
        """Loads dictionary like a Cell from the slice.
        Returns None if the dictionary was null()."""
        not_null = self.read_bit()
        if not_null:
            return self.read_ref()
        else:
            return None

    def preload_dict(self) -> Optional[Cell]:
        not_null = self.preload_bit()
        if not_null:
            return self.preload_ref()
        else:
            return None

    def skip_dict(self):
        self.load_dict()

    @property
    def remaining_bits(self) -> int:
        return len(self.bits)

    @property
    def remaining_refs(self) -> int:
        return len(self.refs) - self.ref_offset

    def as_cell(self):
        return begin_cell().store_slice(self).end_cell()
