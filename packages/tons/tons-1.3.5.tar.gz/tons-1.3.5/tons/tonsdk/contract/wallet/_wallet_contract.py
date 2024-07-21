import decimal
import time
from enum import Enum
from typing import Optional, Set, Union, List, Dict

from pydantic import BaseModel

from .. import Contract
from ...boc import Cell
from ...utils import Address, sign_message, TonCurrencyEnum, to_nano


class WalletVersionEnum(str, Enum):
    v2r1 = 'v2r1'
    v2r2 = 'v2r2'
    v3r1 = 'v3r1'
    v3r2 = 'v3r2'
    v4r1 = 'v4r1'
    v4r2 = 'v4r2'

    @classmethod
    def with_subwallet_id(cls) -> Set[str]:
        return {cls.v3r1.value, cls.v3r2.value, cls.v4r1.value, cls.v4r2.value}


class SendModeEnum(int, Enum):
    carry_all_remaining_balance = 128
    carry_all_remaining_incoming_value = 64
    destroy_account_if_zero = 32
    ignore_errors = 2
    pay_gas_separately = 1


class InternalMessage(BaseModel):
    send_mode: int = SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately
    to_addr: Address
    amount: decimal.Decimal
    currency: TonCurrencyEnum
    body: Optional[Union[str, Cell, bytes]]
    state_init: Optional[Cell]

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True


class WalletContract(Contract):
    def __init__(self, **kwargs):
        if ("public_key" not in kwargs or "private_key" not in kwargs) and "address" not in kwargs:
            raise Exception(
                "WalletContract required publicKey or address in options")
        super().__init__(**kwargs)

    def create_data_cell(self):
        cell = Cell()
        cell.bits.write_uint(0, 32)
        cell.bits.write_bytes(self.options["public_key"])
        return cell

    def create_signing_message(self, seqno=None, valid_until: Optional[int]=None):
        # TODO refactor this
        # if valid_until is not None:
        #     raise ValueError("Valid until is not needed by wallet ver 1")
        seqno = seqno or 0
        cell = Cell()
        cell.bits.write_uint(seqno, 32)
        return cell

    def create_transfer_message(self, seqno: int, messages: List[InternalMessage], dummy_signature=False,
                                timeout: int = 60, timestamp: Optional[float] = None):
        assert len(messages) <= 4, 'Currently supported wallets support a maximum of 4 internal messages'
        timestamp = timestamp or time.time()
        valid_until = int(timestamp) + timeout
        signing_message = self.create_signing_message(seqno, valid_until=valid_until)
        for message in messages:
            payload_cell = Cell()
            if message.body:
                if type(message.body) == str:
                    payload_cell = self.text_message_to_cell(message.body)
                elif hasattr(message.body, 'refs'):
                    payload_cell = message.body
                else:
                    payload_cell.bits.write_bytes(message.body)

            order_header = Contract.create_internal_message_header(
                message.to_addr, to_nano(message.amount, message.currency))
            order = Contract.create_common_msg_info(
                order_header, message.state_init, payload_cell)
            signing_message.bits.write_uint8(message.send_mode)
            signing_message.store_ref(order)

        res = self.create_external_message(signing_message, seqno, dummy_signature)
        if self is not WalletContract:  # not v1
            res['valid_until'] = valid_until
        return res

    def create_external_message(self, signing_message, seqno, dummy_signature=False) -> Dict:
        signature = bytes(64) if dummy_signature else sign_message(
            bytes(signing_message.bytes_hash()), self.options['private_key']).signature

        body = Cell()
        body.bits.write_bytes(signature)
        body.write_cell(signing_message)

        state_init = code = data = None

        if seqno == 0:
            deploy = self.create_state_init()
            state_init = deploy["state_init"]
            code = deploy["code"]
            data = deploy["data"]

        self_address = self.address
        header = Contract.create_external_message_header(self_address)
        result_message = Contract.create_common_msg_info(
            header, state_init, body)

        return {
            "address": self_address,
            "message": result_message,
            "body": body,
            "signature": signature,
            "signing_message": signing_message,
            "state_init": state_init,
            "code": code,
            "data": data,
        }

    def create_init_external_message(self) -> Dict:
        create_state_init = self.create_state_init()
        state_init = create_state_init["state_init"]
        address = create_state_init["address"]
        code = create_state_init["code"]
        data = create_state_init["data"]

        signing_message = self.create_signing_message()
        signature = sign_message(
            bytes(signing_message.bytes_hash()), self.options['private_key']).signature

        body = Cell()
        body.bits.write_bytes(signature)
        body.write_cell(signing_message)

        header = Contract.create_external_message_header(address)
        external_message = Contract.create_common_msg_info(
            header, state_init, body)

        return {
            "address": address,
            "message": external_message,

            "body": body,
            "signing_message": signing_message,
            "state_init": state_init,
            "code": code,
            "data": data,
        }

    @classmethod
    def default_subwallet_id(cls, workchain: int, version: Optional[WalletVersionEnum] = None) \
            -> Optional[int]:
        if version is None or version in WalletVersionEnum.with_subwallet_id():
            return 698983191 + workchain

        return None

    @staticmethod
    def init_amount(version: WalletVersionEnum) -> decimal.Decimal:
        """
        Amount necessary to initialize a wallet.
        :param version: wallet version
        :return: amount (currency - ton)
        """
        if version == WalletVersionEnum.v2r1:
            return decimal.Decimal('0.004295')
        elif version == WalletVersionEnum.v2r2:
            return decimal.Decimal('0.004468')
        elif version == WalletVersionEnum.v3r1:
            return decimal.Decimal('0.004563')
        elif version == WalletVersionEnum.v3r2:
            return decimal.Decimal('0.004760')
        elif version == WalletVersionEnum.v4r1:
            return decimal.Decimal('0.011688')
        elif version == WalletVersionEnum.v4r2:
            return decimal.Decimal('0.011348')
        else:
            raise NotImplementedError(f"Unsupported version: {version}")
