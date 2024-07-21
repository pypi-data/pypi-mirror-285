from datetime import datetime
from functools import lru_cache
from typing import Optional

from PyQt6.QtGui import QColor

from tons.ui.gui.utils import html_text_colored
from ._colors import TransactionColors
from ._item_data import TransactionListItemData, TransactionListItemKind


def get_state_text(data: TransactionListItemData) -> str:
    return __get_state_text(data.kind, data.error)


def __colored(text: str, color: QColor) -> str:
    return html_text_colored(text, color)


@lru_cache(maxsize=256)
def __get_state_text(transaction_state: TransactionListItemKind, transaction_error: Optional[str]) -> str:
    if transaction_state == TransactionListItemKind.error:
        return __colored(transaction_error, TransactionColors().error)
    if transaction_state == TransactionListItemKind.pending:
        return __colored('Pending', TransactionColors().status)
    if transaction_state == TransactionListItemKind.planned:
        return __colored('Planned', TransactionColors().status)
    if transaction_state == TransactionListItemKind.complete:
        return __colored('Complete', TransactionColors().status)

    assert False


def get_time(data: TransactionListItemData, error: bool = False, taken: bool = True):
    return get_start_time(data, error, taken) + get_dash() + get_end_time(data, error, taken)


def get_start_time(data: TransactionListItemData, error: bool = False, taken: bool = True) -> str:
    return __get_formatted_datetime(data.time_start) + '&nbsp;'


def get_dash():
    return __colored('—', TransactionColors().dash)


def get_end_time(data: TransactionListItemData, error: bool = False, taken: bool = True) -> str:
    return '&nbsp;' + __get_formatted_datetime(data.time_finish, error, taken)


@lru_cache(maxsize=256)
def __get_formatted_datetime(datetime_: datetime, error: bool = False, taken: bool = True) -> str:
    time_col = TransactionColors().time
    seconds_col = TransactionColors().seconds
    pending_col = TransactionColors().pending_time

    if error:
        time_col = TransactionColors().error
        seconds_col = TransactionColors().error_seconds
        pending_col = TransactionColors().error_pending

    try:
        return datetime_.strftime(f'{__colored("%H:%M", time_col)}{__colored(":%S", seconds_col)}')
    except AttributeError:
        txt = "pending" if taken else "planned"
        return __colored(txt, pending_col)
