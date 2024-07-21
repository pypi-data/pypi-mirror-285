from abc import ABC
from typing import Optional, Union

from ..boc import Cell
from ..utils import Address


class Contract(ABC):
    def __init__(self, **kwargs):
        self.options = kwargs
        self._address = Address(
            kwargs["address"]) if "address" in kwargs else None
        if "wc" not in kwargs:
            kwargs["wc"] = self._address.wc if self._address is not None else 0

    @property
    def address(self):
        if self._address is None:
            self._address = self.create_state_init()["address"]

        return self._address

    def create_state_init(self):
        code_cell = self.create_code_cell()
        data_cell = self.create_data_cell()
        state_init = self.__create_state_init(code_cell, data_cell)
        state_init_hash = state_init.bytes_hash()

        address = Address(
            str(self.options["wc"]) + ":" + state_init_hash.hex())

        return {
            "code": code_cell,
            "data": data_cell,
            "address": address,
            "state_init": state_init,
        }

    def create_code_cell(self):
        if "code" not in self.options or self.options["code"] is None:
            raise Exception("Contract: options.code is not defined")
        return self.options["code"]

    def create_data_cell(self):
        return Cell()

    @classmethod
    def create_external_message_header(cls, dest, src=None, import_fee=0):
        message = Cell()
        message.bits.write_uint(2, 2)
        message.bits.write_address(Address(src) if src else None)
        message.bits.write_address(Address(dest))
        message.bits.write_grams(import_fee)
        return message

    @classmethod
    def create_internal_message_header(cls,
                                       dest: Address,
                                       grams: int = 0,
                                       ihr_disabled: bool = True,
                                       bounce: Optional[bool] = None,
                                       bounced: bool = False,
                                       src: Optional[Union[Address, str]] = None,
                                       currency_collection: Optional[bool] = None,
                                       ihr_fees: int = 0,
                                       fwd_fees: int = 0,
                                       created_lt: int = 0,
                                       created_at: int = 0):
        message = Cell()
        message.bits.write_bit(0)
        message.bits.write_bit(ihr_disabled)

        if bounce is not None:
            message.bits.write_bit(bounce)
        else:
            message.bits.write_bit(Address(dest).is_bounceable)
        message.bits.write_bit(bounced)
        message.bits.write_address(Address(src) if src else None)
        message.bits.write_address(Address(dest))
        message.bits.write_grams(grams)
        if currency_collection:
            raise NotImplementedError("Currency collections are not implemented yet")

        message.bits.write_bit(bool(currency_collection))
        message.bits.write_grams(ihr_fees)
        message.bits.write_grams(fwd_fees)
        message.bits.write_uint(created_lt, 64)
        message.bits.write_uint(created_at, 32)
        return message

    @classmethod
    def create_common_msg_info(cls, header, state_init=None, body=None):
        common_msg_info = Cell()
        common_msg_info.write_cell(header)
        if state_init:
            common_msg_info.bits.write_bit(1)
            if common_msg_info.bits.get_free_bits() - 1 >= state_init.bits.get_used_bits():
                common_msg_info.bits.write_bit(0)
                common_msg_info.write_cell(state_init)
            else:
                common_msg_info.bits.write_bit(1)
                common_msg_info.store_ref(state_init)
        else:
            common_msg_info.bits.write_bit(0)

        if body:
            if common_msg_info.bits.get_free_bits() >= body.bits.get_used_bits():
                common_msg_info.bits.write_bit(0)
                common_msg_info.write_cell(body)
            else:
                common_msg_info.bits.write_bit(1)
                common_msg_info.store_ref(body)
        else:
            common_msg_info.bits.write_bit(0)

        return common_msg_info

    def __create_state_init(self, code, data, library=None, split_depth=None, ticktock=None):
        if library or split_depth or ticktock:
            raise NotImplementedError("Library/SplitDepth/Ticktock in state init is not implemented")

        state_init = Cell()
        settings = [bool(split_depth), bool(ticktock), bool(code), bool(data), bool(library)]
        state_init.bits.write_bit_array(settings)

        if code:
            state_init.store_ref(code)
        if data:
            state_init.store_ref(data)
        if library:
            state_init.store_ref(library)
        return state_init

    @classmethod
    def text_message_to_cell(cls, text: str) -> Cell:
        payload_cell = Cell()
        payload_cell.bits.write_uint(0, 32)
        payload_bytes = bytes(text, 'utf-8')
        cur_cell = payload_cell
        while (free_bytes := cur_cell.bits.get_free_bytes()) < len(payload_bytes):
            cur_cell.bits.write_bytes(payload_bytes[:free_bytes])
            payload_bytes = payload_bytes[free_bytes:]
            prev_cell = cur_cell
            cur_cell = Cell()
            prev_cell.store_ref(cur_cell)
        cur_cell.bits.write_bytes(payload_bytes)
        return payload_cell