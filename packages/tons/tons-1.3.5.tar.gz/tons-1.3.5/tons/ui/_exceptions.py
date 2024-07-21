from typing import Sequence

from tons.tonclient.utils import WhitelistContactType, contact_type_description


class WhitelistContactAmbiguityError(Exception):
    def __init__(self, *, contact_name: str, contact_types: Sequence[WhitelistContactType]):
        assert len(contact_types) >= 2
        message = f'Contact with the name {contact_name} is ambiguous - found in: '
        message += ', '.join([contact_type_description(contact_type) for contact_type in contact_types])
        super().__init__(message)
