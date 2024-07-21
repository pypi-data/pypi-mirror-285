import decimal
from pydantic import ValidationError
from tons.config._dns import DnsConfig
from tons.tonsdk.crypto import mnemonic_is_valid
from tons.tonsdk.utils import Address, InvalidAddressError


def number_greater_than_or_equal_to_zero(answers, current):
    try:
        return decimal.Decimal(current) >= 0
    except (ValueError, TypeError, decimal.InvalidOperation):
        return False


def valid_workchain(answers, current):
    try:
        return int(current) in [0, -1]
    except (ValueError, TypeError):
        return False


def integer_greater_than_zero(answers, current):
    try:
        return int(current) > 0
    except (ValueError, TypeError):
        return False


def integer_greater_or_equal_than_zero(answers, current):
    try:
        return int(current) >= 0
    except (ValueError, TypeError):
        return False


def valid_dns_refresh_amount(answers, current):
    try:
        DnsConfig(max_expiring_in=current)
    except ValidationError:
        return False
    return True


def non_empty_string(answers, string: str):
    return bool(string)


def valid_mnemonics(answers, current):
    return mnemonic_is_valid(current.split(" "))


def ignore_if_transfer_all(answers):
    return answers["transfer_all"]


def valid_address(answers, current: str):
    try:
        Address(current.strip())
        return True
    except InvalidAddressError:
        return False

