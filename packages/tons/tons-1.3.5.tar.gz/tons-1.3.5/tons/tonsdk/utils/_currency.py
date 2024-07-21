import contextlib
import decimal
from enum import Enum
from typing import Union


@contextlib.contextmanager
def ton_currency_decimal_context():
    """
    Context manager for setting the precision of the decimal module for TON currency calculations.

    This context manager sets the precision of the decimal module, allowing for accurate calculations involving
    TON currency.

    Usage:
        with ton_currency_decimal_context():
            # Perform TON currency calculations with the desired precision

    Note:
        - The decimal module's precision affects the number of digits used for calculations and rounding.
        - The default precision is 28, which is suitable for most general-purpose calculations but may not
          be sufficient for TON currency calculations.
        - This context is used in TONSDK instead of calling `setup_default_decimal_context()`, allowing developers
          to incorporate TONSDK as a framework in their projects without overriding their default decimal context
          globally.

    Returns:
        context: A context manager providing the local decimal context with the desired precision.
    """
    with decimal.localcontext() as ctx:
        ctx.prec = 999
        yield ctx


def setup_default_decimal_context():
    """
    Sets up the default decimal context for TON currency calculations.

    This function should be called only once in the main entry point of the program, before any other TON currency
    calculations take place. It sets the default decimal context's precision to the value provided by the
    `ton_currency_decimal_context` context manager.

    Note:
        - This function sets up the default decimal context for all threads in the program.
        - This function is called in `tons-direct` and `tons-interactive` in the main entry point, setting the default
          decimal context for all subsequent calculations.
    """
    with ton_currency_decimal_context() as ctx:
        decimal.DefaultContext.prec = ctx.prec
    decimal.setcontext(decimal.DefaultContext)


class TonCurrencyEnum(str, Enum):
    nanoton = 'nanoton'
    ton = 'ton'


def validate_nanoton_amount(amount_nano: int):
    """
    Validate the bounds of a TON amount in nanotons.

    Args:
        amount_nano (int): The amount in nanotons to be validated.

    Raises:
        ValueError: If the amount is not within the valid bounds of 0 and 2**120 - 1.

    References:
        - TON blockchain: https://github.com/ton-blockchain/ton/blob/master/crypto/block/block.tlb#L123

    """
    if not (0 <= amount_nano <= 2**120 - 1):
        raise ValueError("Amount of nanoton must be between 0 and 2**120 - 1")


def to_nano(amount: Union[int, str, bytes, bytearray, float, decimal.Decimal], src_unit: TonCurrencyEnum) -> int:
    """
    Converts an amount to nanoton.

    Args:
        amount (Union[int, str, bytes, bytearray, float, decimal.Decimal]): The amount to convert (ton or nanoton)
        src_unit (TonCurrencyEnum): The source unit of the amount.

    Returns:
        int: The converted amount in nanoton.

    Raises:
        ValueError: If the source unit is unknown.

    Note:
        - Supported source units are TonCurrencyEnum.nanoton and TonCurrencyEnum.ton.
        - The conversion factor from coins to nanocoins is 1E+9.
    """
    if isinstance(amount, float):
        amount = str(amount)
    amount = decimal.Decimal(amount)

    with ton_currency_decimal_context():
        if src_unit == TonCurrencyEnum.nanoton:
            result = int(amount)
        elif src_unit == TonCurrencyEnum.ton:
            result = int(decimal.Decimal(amount) * decimal.Decimal('1E+9'))
        else:
            raise ValueError(f"Unknown unit: {src_unit}")

    validate_nanoton_amount(result)
    return result


def from_nano(amount: int, dst_unit: TonCurrencyEnum) -> Union[int, decimal.Decimal]:
    """
    Converts an amount from nanoton.

    Args:
        amount (int): The amount to convert in nanoton.
        dst_unit (TonCurrencyEnum): The destination unit for the converted amount (ton or nanoton).

    Returns:
        Union[int, decimal.Decimal]: The converted amount in the specified destination unit.

    Raises:
        ValueError: If the destination unit is unknown.

    Note:
        - Supported destination units are TonCurrencyEnum.nanoton and TonCurrencyEnum.ton.
        - The conversion factor from nanocoins to coins is 1E-9.
    """
    amount = int(amount)
    validate_nanoton_amount(amount)
    with ton_currency_decimal_context():
        if dst_unit == TonCurrencyEnum.nanoton:
            return amount
        elif dst_unit == TonCurrencyEnum.ton:
            return decimal.Decimal(amount) / decimal.Decimal('1E+9')
        else:
            raise ValueError(f"Unknown unit: {dst_unit}")
