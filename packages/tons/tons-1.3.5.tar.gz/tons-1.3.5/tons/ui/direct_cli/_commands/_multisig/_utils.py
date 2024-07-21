from typing import Optional

from tons.tonclient.utils import RecordDoesNotExistError, Record
from tons.ui._utils import SharedObject
from tons.ui.direct_cli._utils import CustomClickException


def validate_save_as(shared_object: SharedObject, save_as: Optional[str]) -> Optional[str]:
    if save_as:
        existing_contact = shared_object.keystore.whitelist.get_contact(save_as, raise_none=False)
        if existing_contact is not None:
            raise CustomClickException(f'Contact with the name {save_as} already exists')
    return save_as

def validate_record(shared_object: SharedObject, record_name: str) -> Record:
    try:
        record = shared_object.keystore.get_record_by_name(record_name)
    except RecordDoesNotExistError:
        raise CustomClickException(f'Record with the name {record_name} does not exist')
    return record

