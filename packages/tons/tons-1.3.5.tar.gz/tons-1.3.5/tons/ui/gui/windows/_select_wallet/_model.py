import weakref

from PyQt6.QtCore import QObject

from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import CtxReferenceError
from tons.ui.gui.windows.mixins.list_wallets import ListWalletsModel


class SelectWalletModel(QObject, ListWalletsModel):
    def __init__(self, ctx: SharedObject, keystore_name: str):
        super().__init__()
        self.__ctx = weakref.ref(ctx)
        self.init_list_wallets(keystore_name)

    @property
    def ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    @property
    def keystore_name(self):
        return self._keystore.short_name

    @property
    def records_count(self) -> int:
        return len(self._keystore.get_records(False))

