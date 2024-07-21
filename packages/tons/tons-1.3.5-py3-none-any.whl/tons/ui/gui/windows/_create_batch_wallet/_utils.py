from typing import Optional, List

from pydantic import BaseModel

from tons.tonsdk.contract.wallet import WalletVersionEnum


class CreateBatchWalletTaskModel(BaseModel):
    comment: str
    version: WalletVersionEnum
    workchain: int
    min_idx: int
    max_idx: int
    prefix: str
    suffix: str


def range_is_valid(min_idx: Optional[int], max_idx: Optional[int]) -> bool:
    if None in (min_idx, max_idx):
        return False
    if max_idx < min_idx:
        return False
    return True


def range_decimal_places(min_idx: int, max_idx: int) -> int:
    min_idx_str = str(min_idx)
    max_idx_str = str(max_idx)
    return max(len(min_idx_str), len(max_idx_str))


def get_wallet_name(idx: int, prefix: str, suffix: str, min_idx: Optional[int], max_idx: Optional[int]):
    decimal_places = range_decimal_places(min_idx, max_idx)
    pattern = f'%s%0{decimal_places}d%s'
    name = pattern % (prefix, idx, suffix)
    return name


def get_wallet_names(task: CreateBatchWalletTaskModel) -> List[str]:
    wallet_names = []
    for idx in range(task.min_idx, task.max_idx + 1):
        wallet_name = get_wallet_name(idx, task.prefix, task.suffix, task.min_idx, task.max_idx)
        wallet_names.append(wallet_name)
    return wallet_names
