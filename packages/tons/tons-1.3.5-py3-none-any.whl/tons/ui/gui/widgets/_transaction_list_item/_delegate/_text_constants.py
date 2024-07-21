from functools import lru_cache
from typing import Optional

from .._item_data import TransactionButton


@lru_cache
def cancel_button_text() -> str:
    return 'Cancel'

@lru_cache
def edit_and_retry_button_text() -> str:
    return 'Edit and retry...'

@lru_cache
def check_in_scanner_button_text() -> str:
    return 'Check in scanner'

@lru_cache
def get_button_text(button_kind: Optional[TransactionButton]) -> str:
    if button_kind == TransactionButton.edit_and_retry:
        return edit_and_retry_button_text()
    if button_kind == TransactionButton.view_in_scanner:
        return check_in_scanner_button_text()
    if button_kind == TransactionButton.cancel:
        return cancel_button_text()
    return ''
