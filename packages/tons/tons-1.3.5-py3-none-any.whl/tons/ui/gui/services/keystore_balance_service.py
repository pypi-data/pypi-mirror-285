import decimal
import queue
import weakref
from decimal import Decimal
from queue import SimpleQueue
from typing import Optional, Dict, List, Set, Iterable, Tuple

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot, Qt

from tons.logging_ import tons_logger
from tons.tonclient._client._base import AddressInfoResult
from tons.tonclient.utils import KeyStores
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.services import address_info_service, AddressInfoNotFetched
from tons.ui.gui.utils import slot_exc_handler


class KeystoreBalanceNotFetched(GuiException):
    def __init__(self):
        super().__init__("Keystore balance is not yet fetch (wait until 'fetched' signal is emitted)")


class _KeystoreBalanceService(QObject):
    UPDATE_INTERVAL_MS = 1000

    fetched = pyqtSignal(str)  # keystore name
    __update_keystore_balance = pyqtSignal(str)  # keystore name

    def __init__(self, ctx: SharedObject):
        super().__init__()
        self.__ctx = weakref.ref(ctx)

        self._thread = QThread()
        self._thread.setObjectName('keystore balance service thread')
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run)

        self._timer = self._setup_timer()

        self._price_usd: Optional[Decimal] = None
        self._keystore_balance_info: Dict[str, Decimal] = dict()  # key: keystore name with no extension
        self._keystore_address_cache: Dict[str, List[str]] = dict()  # key: keystore name with no extension
        self._keystores_to_update: Set[str] = set()

        self._keystores_to_update_queue: SimpleQueue[str] = SimpleQueue()

        self._setup_signals()

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def _setup_signals(self):
        self.__update_keystore_balance.connect(self._on_update_keystore_balance,
                                               type=Qt.ConnectionType.QueuedConnection)

    def _setup_timer(self) -> QTimer:
        timer = QTimer()
        timer.setInterval(self.UPDATE_INTERVAL_MS)
        timer.timeout.connect(self._update)
        self._thread.finished.connect(timer.stop)
        timer.moveToThread(self._thread)
        return timer

    @pyqtSlot()
    @slot_exc_handler()
    def _run(self):
        self._timer.timeout.emit()
        self._timer.start()

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.quit()
        self._thread.wait()

    def invalidate(self):
        self._keystore_balance_info.clear()
        self._keystore_address_cache.clear()

    def request_update(self, keystore_name: str):
        self._keystores_to_update_queue.put_nowait(keystore_name)

    def request_update_all(self):
        for keystore_name in self.all_keystore_names():
            self._keystores_to_update_queue.put_nowait(keystore_name)

    def balance(self, keystore_name: str) -> Decimal:
        """
        :raises KeystoreBalanceNotFetched
        """
        try:
            return self._keystore_balance_info[self._no_ext(keystore_name)]
        except KeyError:
            raise KeystoreBalanceNotFetched

    @classmethod
    def _no_ext(cls, keystore_name: str) -> str:
        return KeyStores.strip_extension(keystore_name)

    def all_keystore_names(self) -> List[str]:
        return list(map(self._no_ext, self._ctx.keystores.keystore_names))

    def keystore_wallet_addresses(self, keystore_name: str) -> List[str]:
        keystore_name = self._no_ext(keystore_name)
        if keystore_name not in self._keystore_address_cache:
            self._keystore_address_cache[keystore_name] = self._read_keystore_wallet_addresses(keystore_name)
        return self._keystore_address_cache[keystore_name]

    def _read_keystore_wallet_addresses(self, keystore_name: str) -> List[str]:
        keystore = self._ctx.keystores.get_keystore(keystore_name, upgrade=False, raise_none=True)
        addresses = set()
        for record in keystore.get_records(sort_records=False):
            addresses.add(Address.raw_id(record.address))
        return list(addresses)

    def _process_update_queue(self):
        while not self._keystores_to_update_queue.empty():
            try:
                keystore_name = self._keystores_to_update_queue.get_nowait()
            except queue.Empty:
                break
            else:
                try:
                    del self._keystore_address_cache[keystore_name]
                except KeyError:
                    pass
                self._keystores_to_update.add(keystore_name)

    @pyqtSlot()
    @slot_exc_handler()
    def _update(self):
        self._process_update_queue()
        for keystore_name in self.all_keystore_names():
            self.__update_keystore_balance.emit(keystore_name)  # queued connection

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_update_keystore_balance(self, keystore_name: str):
        if keystore_name not in self._keystores_to_update:
            if keystore_name in self._keystore_balance_info:
                return

        tons_logger().debug(f'  update {keystore_name} balance')

        addresses = self.keystore_wallet_addresses(keystore_name)
        address_infos, not_all_balances_fetched = self._get_addresses_info(addresses)
        if not_all_balances_fetched:
            return

        try:
            total_balance = Decimal(sum(addr_info.balance for addr_info in address_infos))
        except (AttributeError, TypeError, ValueError, decimal.InvalidOperation):
            return

        self._keystore_balance_info[keystore_name] = total_balance
        tons_logger().debug(f'balance fetched: {keystore_name} -> {total_balance}')
        self._keystores_to_update.discard(keystore_name)
        self.fetched.emit(keystore_name)

    @classmethod
    def _get_addresses_info(cls, addresses: Iterable[str]) -> Tuple[List[AddressInfoResult], bool]:
        address_infos = []
        not_all_balances_fetched = False
        for addr in addresses:
            try:
                address_info = address_info_service.get(addr)
                address_infos.append(address_info)
            except AddressInfoNotFetched:
                not_all_balances_fetched = True

        return address_infos, not_all_balances_fetched


_keystore_balance_service: Optional[_KeystoreBalanceService] = None


def setup_keystore_balance_service(ctx: SharedObject):
    global _keystore_balance_service
    try:
        _keystore_balance_service.stop()
    except AttributeError:
        pass
    try:
        del _keystore_balance_service
    except NameError:
        pass

    _keystore_balance_service = _KeystoreBalanceService(ctx)
    _keystore_balance_service.start()


def stop_keystore_balance_service():
    global _keystore_balance_service
    try:
        _keystore_balance_service.stop()
    except (NameError, AttributeError):
        pass


class KeystoreBalanceServiceNotInitialized(GuiException):
    def __init__(self):
        super().__init__("Please run setup_keystore_balance_service(ctx) first")


def keystore_balance_service():
    if _keystore_balance_service is None:
        raise KeystoreBalanceServiceNotInitialized
    return _keystore_balance_service


__all__ = ['setup_keystore_balance_service', 'keystore_balance_service', 'KeystoreBalanceServiceNotInitialized']
