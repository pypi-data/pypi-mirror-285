class ContactLocation:
    def __eq__(self, other):
        return type(self) == type(other)


class GlobalWhitelistLocation(ContactLocation):
    def __repr__(self):
        return 'GlobalWhitelistLocation()'


class LocalWhitelistLocation(ContactLocation):
    def __init__(self, keystore_name: str):
        self.keystore_name = keystore_name

    def __repr__(self) -> str:
        return f'LocalWhitelistLocation({repr(self.keystore_name)})'

    def __eq__(self, other: ContactLocation):
        if isinstance(other, LocalWhitelistLocation):
            return self.keystore_name == other.keystore_name
        return False




