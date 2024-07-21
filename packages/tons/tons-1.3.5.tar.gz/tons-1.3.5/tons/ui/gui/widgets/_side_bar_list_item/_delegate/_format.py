from decimal import Decimal
from functools import lru_cache
from typing import Optional

from tons.ui.gui.utils import pretty_balance


@lru_cache(maxsize=1000)
def format_balance(balance: Optional[Decimal]) -> str:
    if balance is None:
        return ''
    if balance > 1000:
        return pretty_balance(balance, 0, gray_decimal_part=False)
    else:
        return pretty_balance(balance, 3, gray_decimal_part=False)