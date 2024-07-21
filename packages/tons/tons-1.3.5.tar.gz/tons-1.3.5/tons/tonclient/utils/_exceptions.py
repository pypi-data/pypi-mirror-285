from typing import Union

from tons.tonsdk.utils import Address


class TonconnectInvalidNetworkError(Exception):
    pass


class TonconnectUnsupportedMethodError(Exception):
    pass


class TonconnectBadRequestError(Exception):
    pass


class TonconnectDifferentNetworkError(Exception):
    pass


class TonconnectWrongMessagesNumberError(Exception):
    pass


class TonconnectWrongRpcRequestIdError(Exception):
    pass


class TonconnectRequestExpiredError(Exception):
    pass


class TonconnectWrongParamsNumberError(Exception):
    pass


class ConnectionAlreadyExistsError(Exception):
    pass


class ConnectionDoesNotExistError(Exception):
    pass


class WhitelistContactAlreadyExistsError(Exception):
    pass


class WhitelistContactNameAlreadyExistsError(WhitelistContactAlreadyExistsError):
    def __init__(self, name: str):
        self.name = name
        desc = f"Contact with the name '{name}' already exists"
        super().__init__(desc)


class WhitelistContactAddressAlreadyExistsError(WhitelistContactAlreadyExistsError):
    def __init__(self, address: str, name: str):
        self.address = address
        self.name = name
        desc = f"Contact with the address {address} already exists: {name}"
        super().__init__(desc)


class WhitelistContactDoesNotExistError(Exception):
    pass


class WhitelistContactNameInvalidError(ValueError):
    pass


class KeyStoreAlreadyExistsError(Exception):
    pass


class KeyStoreDoesNotExistError(Exception):
    pass


class KeyStoreAccessDeniedError(Exception):
    pass


class KeyStoreInvalidPasswordError(Exception):
    pass


class KeyStoreShortPasswordError(KeyStoreInvalidPasswordError):
    def __init__(self, min_symbols: int):
        self.min_symbols = min_symbols
        desc = f"Password must be at least {min_symbols} characters long."
        super().__init__(desc)


class KeyStoreWrongPasswordError(KeyStoreInvalidPasswordError):
    def __init__(self):
        super().__init__('Invalid keystore password.')


class KeyStoreNameInvalidError(ValueError):
    pass


class InvalidKeyStoreError(Exception):
    pass


class InvalidBackupError(Exception):
    pass


class KeyStoreIsNotSpecifiedError(Exception):
    pass


class RecordAlreadyExistsError(Exception):
    pass


class RecordWithNameAlreadyExistsError(RecordAlreadyExistsError):
    def __init__(self, name: str):
        super().__init__(f"Record with the name '{name}' already exists.")
        self.name = name


class RecordWithAddressAlreadyExistsError(RecordAlreadyExistsError):
    def __init__(self, address: str, name: str):
        super().__init__(f"Record with the address '{address}' already exists under name {name}")
        self.name = name
        self.address = address


class RecordDoesNotExistError(Exception):
    pass


class RecordNameInvalidError(ValueError):
    pass


class InvalidMnemonicsError(ValueError):
    pass


class InvalidPrivateKeyError(ValueError):
    pass


class MultiSigRecordDoesNotExistError(Exception):
    pass


class MultiSigRecordAlreadyExistsError(Exception):
    pass


class MultiSigRecordNameInvalid(ValueError):
    pass