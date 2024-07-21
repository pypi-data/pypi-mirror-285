from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from typing import Union, Optional, Tuple, List, Sequence

from colorama import Fore
from pydantic import BaseModel, validator

from ._exceptions import MultiSigRecordDoesNotExistError, MultiSigRecordAlreadyExistsError, MultiSigRecordNameInvalid
from tons.tonsdk.utils import Address, InvalidAddressError


class BaseMultiSigRecord(BaseModel, ABC):
    name: str
    address: Union[Address, str]  # converted to str on validation
    comment: str = ""

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    @validator('name')
    def _validate_name(cls, v) -> str:
        if not v:
            raise MultiSigRecordNameInvalid('Empty record name is not allowed')
        return v

    @validator('address')
    def _validate_address(cls, v: Union[str, Address], values, **kwargs) -> str:
        try:
            return Address(v).to_string()
        except InvalidAddressError as e:
            raise ValueError(e)

    @validator('comment')
    def _validate_comment(cls, v, values, **kwargs) -> str:
        if not v:
            v = ''
        return str(v)

    def address_to_show(self) -> str:
        return Address(self.address).to_string(True, True, True)

    @abstractmethod
    def pretty_string(self) -> str:
        raise NotImplementedError


class MultiSigWalletRecord(BaseMultiSigRecord):
    def pretty_string(self) -> str:
        return f"{Fore.BLUE}(M){Fore.RESET} {self.name}"


class MultiSigOrderRecord(BaseMultiSigRecord):
    def pretty_string(self) -> str:
        return f"{Fore.YELLOW}(O){Fore.RESET} {self.name}"


class BaseMultiSigRecordList(ABC):
    def get_records(self, sort: bool = True) -> Tuple[BaseMultiSigRecord, ...]:
        if sort:
            def key(record: BaseMultiSigRecord):
                return record.name
            return tuple(sorted(self._records(), key=key))
        return tuple(self._records())

    def get_record(self, *, name: Optional[str] = None, address: Union[Address, str, None] = None) -> BaseMultiSigRecord:
        if (name is None) == (address is None):
            raise ValueError('Either name xor address should be specified')

        if name is not None:
            return self._get_record_by_name(name)

        if address is not None:
            return self._get_record_by_address(address)

    def add_record(self, record: BaseMultiSigRecord, validate_does_not_exist: bool = True):
        if validate_does_not_exist:
            self._validate_record_with_name_does_not_exist(record.name)
            self._validate_record_with_address_does_not_exist(record.address)
        self._add_record(record)

    def _add_record(self, record: BaseMultiSigRecord):
        self._records().append(record)

    def _set_records(self, records: Sequence[BaseMultiSigRecord], validate_does_not_exist: bool = True):
        self._records().clear()
        for record in records:
            self.add_record(record, validate_does_not_exist)

    def edit_record(self, name: str, *,
                    new_name: Optional[str] = None,
                    new_address: Union[str, Address, None] = None,
                    new_comment: Optional[str] = None):
        record_idx = self._get_record_idx_by_name(name)
        record = self._records()[record_idx]

        with self._restore_record_on_failure(record_idx):
            if new_name is not None:
                if record.name != new_name:
                    self._validate_record_with_name_does_not_exist(new_name)
                self._records()[record_idx].name = new_name

            if new_address is not None:
                if Address(record.address) != Address(new_address):
                    self._validate_record_with_address_does_not_exist(new_address)
                self._records()[record_idx].address = new_address

            if new_comment is not None:
                self._records()[record_idx].comment = new_comment

    def delete_record(self, *,
                      name: Optional[str] = None,
                      record: Optional[BaseMultiSigRecord] = None,
                      record_idx: Optional[int] = None):
        if [name, record, record_idx].count(None) != 2:
            raise ValueError("Either name, record, xor record_idx should be specified")

        if name is not None:
            idx = self._get_record_idx_by_name(name)
            return self._delete_record_by_idx(idx)

        if record is not None:
            idx = self._records().index(record)
            return self._delete_record_by_idx(idx)

        assert record_idx is not None
        self._delete_record_by_idx(record_idx)


    def _delete_record_by_idx(self, record_idx: int):
        del self._records()[record_idx]


    @contextmanager
    def _restore_record_on_failure(self, record_idx: int):
        record_before = deepcopy(self._records()[record_idx])
        try:
            yield
        except:
            self._records()[record_idx] = record_before
            raise

    @contextmanager
    def restore_on_failure(self):
        records_before = deepcopy(self.get_records())
        try:
            yield
        except:
            self._set_records(records_before, validate_does_not_exist=False)
            raise

    def _validate_record_with_name_does_not_exist(self, name: str):
        try:
            self._get_record_by_name(name)
        except MultiSigRecordDoesNotExistError:
            pass
        else:
            raise MultiSigRecordAlreadyExistsError(f"Record with name {name} already exists")

    def _validate_record_with_address_does_not_exist(self, address: Union[str, Address]):
        try:
            self._get_record_by_address(address)
        except MultiSigRecordDoesNotExistError:
            pass
        else:
            raise MultiSigRecordAlreadyExistsError(f"Record with address {address} already exists")

    def _get_record_by_name(self, name: str) -> BaseMultiSigRecord:
        i = self._get_record_idx_by_name(name)
        return self._records()[i]

    def _get_record_idx_by_name(self, name: str) -> int:
        for i, w in enumerate(self._records()):
            if w.name == name:
                return i
        raise MultiSigRecordDoesNotExistError(f'Record with name {name} does not exist')

    def _get_record_by_address(self, address: Union[Address, str]) -> BaseMultiSigRecord:
        i = self._get_record_idx_by_address(address)
        return self._records()[i]

    def _get_record_idx_by_address(self, address: Union[Address, str]) -> int:
        for i, w in enumerate(self._records()):
            if Address(w.address) == Address(address):
                return i
        raise MultiSigRecordDoesNotExistError(f"Record with address {address} does not exist")

    @abstractmethod
    def _records(self) -> List[BaseMultiSigRecord]:
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError


class MultiSigWalletList(BaseMultiSigRecordList):
    def add_record(self, record: MultiSigWalletRecord, validate_does_not_exist: bool = True):
        super().add_record(record, validate_does_not_exist)

    def get_records(self, sort: bool = True) -> Tuple[MultiSigWalletRecord, ...]:
        records = super().get_records(sort)
        assert isinstance(records, tuple) and all(isinstance(r, MultiSigWalletRecord) for r in records)
        return records

    def get_record(self, *, name: Optional[str] = None,
                   address: Union[Address, str, None] = None) -> MultiSigWalletRecord:
        record = super().get_record(name=name, address=address)
        assert isinstance(record, MultiSigWalletRecord)
        return record

    def delete_record(self, *,
                      name: Optional[str] = None,
                      record: Optional[MultiSigWalletRecord] = None,
                      record_idx: Optional[int] = None):
        super().delete_record(name=name, record=record, record_idx=record_idx)

    def _records(self) -> List[MultiSigWalletRecord]:
        return self._wallets()

    @abstractmethod
    def _wallets(self) -> List[MultiSigWalletRecord]:
        raise NotImplementedError


class MultiSigOrderList(BaseMultiSigRecordList):
    def add_record(self, record: MultiSigOrderRecord, validate_does_not_exist: bool = True):
        super().add_record(record, validate_does_not_exist)

    def get_records(self, sort: bool = True) -> Tuple[MultiSigOrderRecord, ...]:
        records = super().get_records(sort)
        assert isinstance(records, tuple) and all(isinstance(r, MultiSigOrderRecord) for r in records)
        return records

    def _records(self) -> List[MultiSigOrderRecord]:
        return self._orders()

    @abstractmethod
    def _orders(self) -> List[MultiSigOrderRecord]:
        raise NotImplementedError


class LocalMultiSigRecordList(BaseMultiSigRecordList):
    def __init__(self, keystore: 'BaseKeyStore'):
        self._keystore: 'BaseKeyStore' = keystore

    def save(self):
        self._keystore.save()


class LocalMultiSigWalletList(MultiSigWalletList, LocalMultiSigRecordList):
    def __init__(self, keystore: 'BaseKeyStore'):
        LocalMultiSigRecordList.__init__(self, keystore)

    def _wallets(self) -> List[MultiSigWalletRecord]:
        return self._keystore.multisig_wallets


class LocalMultiSigOrderList(MultiSigOrderList, LocalMultiSigRecordList):
    def __init__(self, keystore: 'BaseKeyStore'):
        LocalMultiSigRecordList.__init__(self, keystore)

    def _orders(self) -> List[MultiSigOrderRecord]:
        return self._keystore.multisig_orders


__all__ = ['MultiSigOrderRecord', 'MultiSigWalletRecord', 'LocalMultiSigWalletList', 'LocalMultiSigOrderList']