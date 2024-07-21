import dataclasses
import random
from datetime import datetime
from enum import Enum
from typing import List, Union, Tuple, Dict, Optional, Sequence

from tons.tonsdk.boc import Cell, begin_cell
from tons.tonsdk.contract import Contract
from ._constants import _MULTISIG_CODE, _BitSize

from tons.tonsdk.utils import Address
from ._utils import addresses_to_cell, cell_to_addresses, dict_to_list


@dataclasses.dataclass
class MultiSigConfig:
    threshold: int
    signers: Sequence[Union[Address, str]]
    proposers: Optional[Sequence[Union[Address, str]]]
    allow_arbitrary_seqno: bool
    initial_seqno: int = 0

    def __post_init__(self):
        if len(self.signers) >= (1 << _BitSize.SIGNER_INDEX) or len(self.signers) == 0:
            raise ValueError('Invalid signers')

        self.proposers = self.proposers or []
        if len(self.proposers) >= (1 << _BitSize.SIGNER_INDEX):
            raise ValueError('Invalid proposers')

        if self.threshold <= 0 or self.threshold > len(self.signers):
            raise ValueError("Invalid threshold - expected 1 <= threshold <= len(signers)")

        _validate_order_seqno(self.initial_seqno)
        self.signers = [Address(a) for a in self.signers]
        self.proposers = [Address(a) for a in self.proposers]

def _validate_order_seqno(order_seqno: int):
    if order_seqno < 0 or order_seqno > (1 << _BitSize.ORDER_SEQNO):
        raise ValueError('Invalid seqno')


class ArbitraryOrderSeqnoGenerateStrategy(str, Enum):
    random = 'random'
    time = 'time'


def _generate_arbitrary_seqno(strategy: ArbitraryOrderSeqnoGenerateStrategy):
    if strategy == ArbitraryOrderSeqnoGenerateStrategy.random:
        return _generate_random_seqno()
    elif strategy == ArbitraryOrderSeqnoGenerateStrategy.time:
        return _generate_seqno_from_timestamp()
    else:
        raise NotImplementedError

def _generate_random_seqno() -> int:
    max_val = (1 << _BitSize.ORDER_SEQNO) - 1
    order_seqno = random.randint(0, max_val)
    return order_seqno

def _generate_seqno_from_timestamp() -> int:
    order_seqno = int(datetime.now().timestamp() * 1e6)
    return order_seqno

@dataclasses.dataclass
class MultiSigInfo:
    next_order_seqno: Optional[int]
    threshold: int
    signers: Sequence[Union[Address, str]]
    proposers: Optional[Sequence[Union[Address, str]]]
    allow_arbitrary_seqno: bool
    initial_seqno: int = 0

    @classmethod
    def from_data_cell(cls, data: Cell):
        next_order_seqno, threshold, signers, signers_num, proposers, allow_arbitrary_seqno = cls._load_data(data)
        if signers_num != len(signers):
            raise ValueError("Inconsistent data")
        signers = dict_to_list(signers)
        if signers_num < 1:
            raise ValueError("Invalid signers")
        proposers = dict_to_list(proposers)
        if allow_arbitrary_seqno:
            next_order_seqno = None

        return cls(
            next_order_seqno=next_order_seqno,
            threshold=threshold,
            signers=signers,
            proposers=proposers,
            allow_arbitrary_seqno=allow_arbitrary_seqno
        )


    @classmethod
    def _load_data(cls, data: Cell) -> Tuple[int, int, Dict[int, Address], int, Dict[int, Address], bool]:
        ds = data.begin_parse()
        next_order_seqno = ds.read_uint(_BitSize.ORDER_SEQNO)
        threshold = ds.read_uint(_BitSize.SIGNER_INDEX)
        signers = cell_to_addresses(ds.read_ref())
        signers_num = ds.read_uint(_BitSize.SIGNER_INDEX)
        proposers = cell_to_addresses(ds.read_maybe_ref())
        allow_arbitrary_seqno = bool(ds.read_bit())

        return next_order_seqno, threshold, signers, signers_num, proposers, allow_arbitrary_seqno

    def __post_init__(self):
        assert self.allow_arbitrary_seqno == (self.next_order_seqno is None)

    def get_next_order_seqno(self, arbitrary_generate_strategy: ArbitraryOrderSeqnoGenerateStrategy = 'random') -> int:
        if not self.allow_arbitrary_seqno:
            order_seqno = self.next_order_seqno
        else:
            order_seqno = _generate_arbitrary_seqno(arbitrary_generate_strategy)
        _validate_order_seqno(order_seqno)
        return order_seqno

    def validate_order_seqno(self, order_seqno: int):
        _validate_order_seqno(order_seqno)
        if self.allow_arbitrary_seqno:
            return
        if order_seqno != self.next_order_seqno:
            raise ValueError(f'Invalid seqno: expected {self.next_order_seqno}')

    def get_is_signer_and_address_idx(self, address: Union[str, Address]) -> Tuple[bool, Optional[int]]:
        """
        :return:
            is_signer
            address_idx - signer or proposer idx, None if neither
        """
        address = Address(address)
        try:
            address_idx = self.signers.index(address)
        except ValueError:
            pass
        else:
            return True, address_idx

        try:
            address_idx = self.proposers.index(address)
        except ValueError:
            pass
        else:
            return False, address_idx

        return False, None


class MultiSigWalletContractV2(Contract):
    def __init__(self, *, config: MultiSigConfig, **kwargs):
        self.code = _MULTISIG_CODE
        self.config = config
        kwargs["code"] = Cell.one_from_boc(self.code)
        super().__init__(**kwargs)


    def create_data_cell(self) -> Cell:
        return (
            begin_cell()
            .store_uint(self.config.initial_seqno, _BitSize.ORDER_SEQNO)
            .store_uint(self.config.threshold, _BitSize.SIGNER_INDEX)
            .store_ref(addresses_to_cell(self.config.signers))  # store non-empty dict
                                                                # .storeRef(beginCell().storeDictDirect(arrayToCell(config.signers)))
            .store_uint(len(self.config.signers), _BitSize.SIGNER_INDEX)
            .store_maybe_ref(addresses_to_cell(self.config.proposers))  # store dict
                                                                        # .storeDict(arrayToCell(config.proposers))
            .store_bit(self.config.allow_arbitrary_seqno)
            .end_cell()
        )

    def create_init_external_message(self):
        create_state_init = self.create_state_init()
        state_init = create_state_init["state_init"]
        address = create_state_init["address"]
        code = create_state_init["code"]
        data = create_state_init["data"]

        body = Cell()

        header = Contract.create_external_message_header(address)
        external_message = Contract.create_common_msg_info(header, state_init, body)

        return {
            "address": address,
            "message": external_message,
            "body": body,
            "state_init": state_init,
            "code": code,
            "data": data,
        }


__all__ = ['MultiSigConfig', 'MultiSigInfo', 'MultiSigWalletContractV2']
