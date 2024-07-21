import dataclasses
import datetime
import decimal
from typing import Sequence, Union, Optional, List

from tons.tonsdk.boc import Cell, begin_cell, begin_dict, MessageRelaxed, CommonMessageInfoRelaxedInternal, \
    CurrencyCollection, Slice
from tons.tonsdk.boc.dict.deserialize_dict import parse_dict
from ._constants import _ORDER_MAX_SEQNO, _BitSize, _ORDER_CODE, _Op
from tons.tonsdk.utils import Address, TonCurrencyEnum, to_nano
from .._wallet_contract import SendModeEnum
from ._utils import addresses_to_cell, cell_to_addresses, dict_to_list


def get_multisig_order_address(multisig_address: Address, order_seqno: int = _ORDER_MAX_SEQNO) -> Address:
    order_state_init = calculate_order_state_init(multisig_address, order_seqno)
    state_init_hash = order_state_init.bytes_hash().hex()
    return Address(f'{multisig_address.wc}:{state_init_hash}')


def pack_order_init_data(multisig_address: Address, order_seqno: int) -> Cell:
    c = begin_cell()
    c.store_address(multisig_address)
    c.store_uint(order_seqno, _BitSize.ORDER_SEQNO)
    return c.end_cell()


def calculate_order_state_init(multisig_address: Address, order_seqno: int = _ORDER_MAX_SEQNO) -> Cell:
    c = begin_cell()
    c.store_uint(0, 2)  # 0b00 - No split_depth; No special
    c.store_maybe_ref(Cell.one_from_boc(_ORDER_CODE))
    c.store_maybe_ref(pack_order_init_data(multisig_address, order_seqno))
    c.store_uint(0, 1) # Empty libraries
    return c.end_cell()


@dataclasses.dataclass
class MultiSigTransferRequest:
    message: Union[MessageRelaxed, Cell]
    send_mode: int = SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately

    @classmethod
    def send_ton(cls,
                 amount: Union[int, decimal.Decimal],
                 currency: TonCurrencyEnum,
                 src: Union[Address, str],
                 dest: Union[Address, str],
                 body: Optional[Cell] = None,
                 init: Optional[Cell] = None,
                 send_mode: int = SendModeEnum.ignore_errors | SendModeEnum.pay_gas_separately) -> 'MultiSigTransferRequest':
        mi = CommonMessageInfoRelaxedInternal(
            ihr_disabled=False,
            bounce=False,
            bounced=False,
            src=Address(src),
            dest=Address(dest),
            value=CurrencyCollection(coins=to_nano(amount, currency)),
            ihr_fee=0,
            forward_fee=0,
            created_lt=0,
            created_at=0
        )
        body = body or Cell()
        mr = MessageRelaxed(info=mi,
                            body=body,
                            init=init)
        return cls(message=mr,
                   send_mode=send_mode)



    # @classmethod
    # def send_ton(cls, message: InternalMessage) -> 'TransferRequest':
    #     payload_cell = Cell()
    #
    #     if message.body:
    #         if type(message.body) == str:
    #             payload_cell.bits.write_uint(0, 32)
    #             payload_bytes = bytes(message.body, 'utf-8')
    #             cur_cell = payload_cell
    #             while (free_bytes := cur_cell.bits.get_free_bytes()) < len(payload_bytes):
    #                 cur_cell.bits.write_bytes(payload_bytes[:free_bytes])
    #                 payload_bytes = payload_bytes[free_bytes:]
    #                 prev_cell = cur_cell
    #                 cur_cell = Cell()
    #                 prev_cell.store_ref(cur_cell)
    #             cur_cell.bits.write_bytes(payload_bytes)
    #         elif hasattr(message.body, 'refs'):
    #             payload_cell = message.body
    #         else:
    #             payload_cell.bits.write_bytes(message.body)
    #
    #     order_header = Contract.create_internal_message_header(
    #         message.to_addr, to_nano(message.amount, message.currency))
    #     order = Contract.create_common_msg_info(
    #         order_header, message.state_init, payload_cell)
    #
    #     return cls(message=order, send_mode=message.send_mode)


@dataclasses.dataclass
class MultiSigUpdateRequest:
    threshold: int
    signers: Sequence[Union[Address, str]]
    proposers: Optional[Sequence[Union[Address, str]]]

    def __post_init__(self):
        if len(self.signers) > 255 or len(self.signers) == 0:
            raise ValueError('Invalid signers')
        self.proposers = self.proposers or []
        if len(self.proposers) > 255:
            raise ValueError('Invalid proposers')
        if self.threshold <= 0 or self.threshold > len(self.signers):
            raise ValueError("Invalid threshold - expected 1 <= threshold <= len(signers)")

        self.signers = [Address(a) for a in self.signers]
        self.proposers = [Address(a) for a in self.proposers]


def pack_multisig_order(actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]]) -> Cell:
    if len(actions) > 255:
        raise ValueError("For action chains above 255 use pack_large")

    d = begin_dict(8)
    for i, action in enumerate(actions):
        if isinstance(action, MultiSigTransferRequest):
            pack = pack_transfer_request
        elif isinstance(action, MultiSigUpdateRequest):
            pack = pack_update_request
        else:
            raise ValueError(f"Unknown request type: {type(action)}")
        d.store_cell(i, pack(action))

    def serializer(src, dest):
        dest.store_ref(src)

    return d.end_cell(serializer=serializer)


def parse_order(cell: Cell) -> List[Union[MultiSigTransferRequest, MultiSigUpdateRequest]]:  # TODO add raise error
    s = cell.begin_parse()
    actions_dict = parse_dict(s, 8, parse_action)

    actions_list = dict_to_list(actions_dict)
    return actions_list


def pack_large():
    raise NotImplementedError


def new_multisig_order_body(actions: Sequence[Union[MultiSigTransferRequest, MultiSigUpdateRequest]], expiration_date: int,
                            is_signer: bool, address_idx: int, query_id: int = 0,
                            order_id: int = _ORDER_MAX_SEQNO) -> Cell:
    c = begin_cell()
    c.store_uint(_Op.NEW_ORDER, _BitSize.OP)
    c.store_uint(query_id, _BitSize.QUERY_ID)
    c.store_uint(order_id, _BitSize.ORDER_SEQNO)
    c.store_bit(is_signer)
    c.store_uint(address_idx, _BitSize.SIGNER_INDEX)
    c.store_uint(expiration_date, _BitSize.TIME)
    packed_order = pack_multisig_order(actions)
    c.store_ref(packed_order)
    return c.end_cell()


def pack_transfer_request(request: MultiSigTransferRequest) -> Cell:
    if isinstance(request.message, Cell):
        message = request.message
    else:
        message = begin_cell().store_message_relaxed(request.message).end_cell()

    c = begin_cell()
    c.store_uint(_Op.SEND_MESSAGE, _BitSize.OP)
    c.store_uint(request.send_mode, 8)
    c.store_ref(message)
    return c.end_cell()


def pack_update_request(request: MultiSigUpdateRequest) -> Cell:
    c = begin_cell()
    c.store_uint(_Op.UPDATE_MULTISIG_PARAMS, _BitSize.OP)
    c.store_uint(request.threshold, _BitSize.SIGNER_INDEX)
    c.store_ref(addresses_to_cell(request.signers))
    c.store_maybe_ref(addresses_to_cell(request.proposers))
    return c.end_cell()

def pack_multisig_order_approve(signer_idx: int, query_id: int = 0) -> Cell:
    c = begin_cell()
    c.store_uint(_Op.APPROVE, _BitSize.OP)
    c.store_uint(query_id, _BitSize.QUERY_ID)
    c.store_uint(signer_idx, _BitSize.SIGNER_INDEX)
    return c.end_cell()


def parse_action(slice_: Slice) -> Union[MultiSigTransferRequest, MultiSigUpdateRequest, None]:
    action_cell = slice_.read_ref()
    s = action_cell.begin_parse()
    op = s.read_uint(_BitSize.OP)
    if op == _Op.SEND_MESSAGE:
        return parse_transfer_request(s)
    elif op == _Op.UPDATE_MULTISIG_PARAMS:
        return parse_update_request(s)
    return  # unknown OpCode

def parse_transfer_request(s: Slice, raise_message_parse_fail: bool = False) -> MultiSigTransferRequest:
    send_mode = s.read_uint(8)
    message = s.read_ref()
    try:
        message = message.begin_parse().read_message_relaxed()
    except Exception as exc: # failed to parse relaxed message, store it as a cell
        if raise_message_parse_fail:
            raise exc

    return MultiSigTransferRequest(message=message, send_mode=send_mode)


def parse_update_request(s: Slice) -> MultiSigUpdateRequest:
    threshold = s.read_uint(_BitSize.SIGNER_INDEX)

    signers = s.read_ref()
    signers = cell_to_addresses(signers)
    signers = dict_to_list(signers)

    proposers = s.read_maybe_ref()
    proposers = cell_to_addresses(proposers)
    proposers = dict_to_list(proposers)

    return MultiSigUpdateRequest(
        threshold=threshold,
        signers=signers,
        proposers=proposers
    )

@dataclasses.dataclass
class MultiSigOrderData:
    multisig_address: Optional[Address]
    order_seqno: int
    threshold: int
    executed: bool
    signers: List[Address]  # indexes matter
    approvals_mask: int
    approvals_num: int
    expiration_date: int
    order: Cell
    actions: Optional[List[Union[MultiSigTransferRequest, MultiSigUpdateRequest, None]]]  # None: failed to parse actions

    @classmethod
    def from_data_cell(cls, data: Cell, raise_actions_parse_fail: bool = False) -> 'MultiSigOrderData':
        return parse_order_data(data, raise_actions_parse_fail)

    def approved_by(self, signer_idx: int) -> bool:
        return bool(self.approvals_mask & (1 << signer_idx))

    def expiration_utc_datetime(self) -> datetime.datetime:
        dt = datetime.datetime.utcfromtimestamp(self.expiration_date)
        return dt

    def failed_to_parse_actions(self) -> bool:
        if self.actions is None:
            return True

        return any([a is None for a in self.actions])

    def expired(self) -> bool:
        return datetime.datetime.utcnow() > self.expiration_utc_datetime()


def parse_order_data(data: Cell, raise_actions_parse_fail: bool = False) -> MultiSigOrderData:
    s = Slice(data)
    multisig_address = s.read_msg_addr()
    order_seqno = s.read_uint(_BitSize.ORDER_SEQNO)
    threshold = s.read_uint(_BitSize.SIGNER_INDEX)
    executed = bool(s.read_bit())
    signers = s.read_ref()
    signers = cell_to_addresses(signers)
    signers = dict_to_list(signers)
    approvals_mask = s.read_uint(_BitSize.MASK_SIZE)
    approvals_num = s.read_uint(_BitSize.SIGNER_INDEX)

    approvals_mask_01 = bin(approvals_mask)[2:]
    if not approvals_num == approvals_mask_01.count('1'):
        raise ValueError("Inconsistent approvals information")

    expiration_date = s.read_uint(_BitSize.TIME)
    order = s.read_ref()

    try:
        actions = parse_order(order)
    except Exception as exc:
        actions = None
        if raise_actions_parse_fail:
            raise exc

    return MultiSigOrderData(
        multisig_address=multisig_address,
        order_seqno=order_seqno,
        threshold=threshold,
        executed=executed,
        signers=signers,
        approvals_mask=approvals_mask,
        approvals_num=approvals_num,
        expiration_date=expiration_date,
        order=order,
        actions=actions
    )


__all__ = ['pack_transfer_request', 'new_multisig_order_body', 'pack_multisig_order', 'MultiSigTransferRequest', 'MultiSigUpdateRequest',
           'calculate_order_state_init', 'pack_multisig_order_approve',
           'pack_order_init_data', 'get_multisig_order_address', 'parse_order_data',
           'MultiSigOrderData']
