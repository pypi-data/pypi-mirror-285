import copy
import math
from typing import Union, Optional, List

from ..utils._address import Address


class BitString:
    def __init__(self, length: int):
        self.array = bytearray(math.ceil(length / 8))
        self.cursor = 0
        self.length = length

    def to_string(self) -> str:
        def to_hex(ba: bytearray) -> str:
            return ''.join(format(x, '02x') for x in ba).upper()
        padded = self.get_top_upped_array()
        if self.cursor % 4 == 0:
            s = to_hex(padded[0:math.ceil(self.cursor / 8)])
            if self.cursor % 8 == 0:
                return s
            return s[:-1]

        s = to_hex(padded)
        if self.cursor % 8 <= 4:
            return s[:-1] + '_'
        return s + '_'



    def __repr__(self):
        return str(self.get_top_upped_array())

    def __iter__(self):
        for i in range(self.cursor):
            yield self.get(i)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start if key.start else 0
            stop = key.stop if key.stop else len(self)
            step = key.step if key.step else 1

            return [self[ii] for ii in range(start, stop, step)]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError("The index (%d) is out of range." % key)
            return self.get(key)
        else:
            raise TypeError("Invalid argument type.")

    def __len__(self):
        return self.length

    def get(self, n: int):
        """Just returns n bits from cursor. Does not move the cursor."""
        return int((self.array[(n // 8) | 0] & (1 << (7 - (n % 8)))) > 0)

    def __off(self, n):
        """Sets next from cursor n bits to 0. Does not move cursor."""
        self.check_range(n)
        self.array[(n // 8) | 0] &= ~(1 << (7 - (n % 8)))

    def __on(self, n):
        """Sets next from cursor n bits to 1. Does not move cursor."""
        self.check_range(n)
        self.array[(n // 8) | 0] |= 1 << (7 - (n % 8))

    def check_range(self, n: int) -> None:
        """Throws an exception if the cursor + n is out of range."""
        if n > self.length:
            raise OverflowError("BitString overflow")

    @classmethod
    def from_top_upped_array(cls, array: bytearray, fulfilled_bytes=True) -> 'BitString':
        """
        Constructs a BitString object from an array that possibly contains an incomplete group of 8 bits and an end bit.

        Args:
            array (bytearray):
                The byte array to set as the data.
            fulfilled_bytes (bool, optional):
                A flag specifying whether the last group of 8 bits in the array is filled.
                If set to False, this method will search for an end bit, erase it, and set the length accordingly.

        Raises:
            ValueError: If the end bit is not found in the array when `fulfilled_bytes` is set to False.

        Returns:
            BitString: The constructed BitString object.
        """
        obj = cls(len(array) * 8)
        obj.array = array
        obj.cursor = obj.length

        if fulfilled_bytes or not obj.length:
            return obj

        for c in range(7):
            obj.cursor -= 1
            if obj.get(obj.cursor):
                obj.__off(obj.cursor)
                break
        else:
            raise ValueError(f"Incorrect TopUppedArray {array}, {fulfilled_bytes}")

        return obj

    def get_top_upped_array(self) -> bytearray:
        """
        Returns a byte array with the appended end bit for data with an incomplete group of 8 bits.
        """
        ret = copy.deepcopy(self)
        ret.length = math.ceil(ret.length / 8) * 8
        bits_to_fill = math.ceil(ret.cursor / 8) * 8 - ret.cursor
        if bits_to_fill > 0:
            bits_to_fill -= 1
            ret.write_bit(1)
            while bits_to_fill > 0:
                bits_to_fill -= 1
                ret.write_bit(0)
        ret.array = ret.array[:math.ceil(ret.cursor / 8)]
        return ret.array

    def get_free_bits(self) -> int:
        """Returns the number of not used bits in the BitString."""
        return self.length - self.cursor

    def get_free_bytes(self) -> int:
        return self.get_free_bits() // 8

    def get_used_bits(self) -> int:
        return self.cursor

    def write_bit_array(self, bit_array: List[bool]):
        """
        Writes a list of boolean values representing a bit array.

        Args:
            bit_array (List[bool]): The list of boolean values representing the bit array.
        """
        for b in bit_array:
            self.write_bit(b)

    def write_bit(self, b: Union[int, bool]):
        b = int(b)
        if b == 1:
            self.__on(self.cursor)
        elif b == 0:
            self.__off(self.cursor)
        else:
            raise ValueError("BitString can only write 1 or 0")

        self.cursor += 1

    def write_uint(self, number: int, bit_length: int):
        if bit_length < 0:
            raise ValueError("bit_length cannot be negative")

        if bit_length == 0 or len("{0:b}".format(number)) > bit_length:
            if number == 0:
                return

            raise ValueError(
                f"bitLength is too small for number, got number={number},bitLength={bit_length}")

        for i in range(bit_length, 0, -1):
            k = (2 ** (i - 1))
            if number // k == 1:
                self.write_bit(1)
                number -= k
            else:
                self.write_bit(0)

    def write_uint8(self, ui8: int):
        """Just as write_uint(n, 8), but only write_uint8(n) (?)."""
        self.write_uint(ui8, 8)

    def write_int(self, number: int, bit_length: int):
        if bit_length < 0:
            raise ValueError("bit_length cannot be negative")

        if bit_length == 1:
            if number == -1:
                self.write_bit(1)
                return

            if number == 0:
                self.write_bit(0)
                return

            raise ValueError("bit_length is too small for the number")
        else:
            if number < 0:
                self.write_bit(1)
                s = 2 ** (bit_length - 1)
                self.write_uint(s + number, bit_length - 1)
            else:
                self.write_bit(0)
                self.write_uint(number, bit_length - 1)

    def write_string(self, value: str):
        self.write_bytes(bytes(value, encoding="utf-8"))

    def write_bytes(self, ui8_array: bytes):
        for ui8 in ui8_array:
            self.write_uint8(ui8)

    def write_bit_string(self, another_bit_string: "BitString"):
        for bit in another_bit_string:
            self.write_bit(bit)

    def write_address(self, address: Optional[Address]):
        """Writes an address, maybe zero-address (None) to the BitString."""
        if address is None:
            self.write_uint(0, 2)
        else:
            self.write_uint(2, 2)
            self.write_uint(0, 1)  # anycast
            self.write_int(address.wc, 8)
            self.write_bytes(address.hash_part)

    def write_grams(self, amount: int):
        if amount == 0:
            self.write_uint(0, 4)
        else:
            amount = int(amount)
            length = math.ceil(len(hex(amount)[2:]) / 2)
            self.write_uint(length, 4)
            self.write_uint(amount, length * 8)

    def write_coins(self, amount: int):
        self.write_grams(amount)
