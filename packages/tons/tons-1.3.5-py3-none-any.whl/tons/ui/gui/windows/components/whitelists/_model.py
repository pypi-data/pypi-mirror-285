import weakref
from typing import List, Tuple

from tons.tonclient.utils import BaseWhitelist
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import CtxReferenceError
from tons.ui.gui.utils import ContactLocation, GlobalWhitelistLocation, LocalWhitelistLocation


class WhitelistsModelComponent:
    def __init__(self, ctx: SharedObject):
        self.__ctx = weakref.ref(ctx)

    def setup(self, ctx: SharedObject):
        self.__ctx = weakref.ref(ctx)

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def get_whitelist(self, contact_location: ContactLocation) -> BaseWhitelist:
        if isinstance(contact_location, GlobalWhitelistLocation):
            return self._ctx.whitelist
        elif isinstance(contact_location, LocalWhitelistLocation):
            keystore_name = contact_location.keystore_name
            keystore = self._ctx.keystores.get_keystore(keystore_name)
            whitelist = keystore.whitelist
            return whitelist
        else:
            raise NotImplementedError('Unknown whitelist sort')

    def get_locations(self) -> Tuple[ContactLocation, ...]:
        keystore_names = self._ctx.keystores.keystore_names
        locations: List[ContactLocation] = []
        locations += [GlobalWhitelistLocation()]
        locations += [LocalWhitelistLocation(keystore_name) for keystore_name in keystore_names]
        return tuple(locations)
