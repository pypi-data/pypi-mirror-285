import weakref
from typing import Optional, Dict

from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

from tons.logging_ import tons_logger
from tons.tonclient import TonError
from tons.tonclient._client._base import TransactionInfo
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.utils import slot_exc_handler


class TxInfoNotFetched(GuiException):
    def __init__(self, tx_hash: Optional[str] = None):
        super().__init__(f"Tx info not fetched {tx_hash or ''}")


class _TxInfoService(QObject):
    fetched = pyqtSignal(str)     # should be emitted only when a new tx info is actually fetched
                                  # (might cause a locking loop otherwise)
    _sig_fetch = pyqtSignal(str)

    def __init__(self, ctx: SharedObject):
        super().__init__()
        self.__ctx = weakref.ref(ctx)

        self._thread = QThread()
        self._thread.setObjectName('transaction info service thread')
        self.moveToThread(self._thread)

        self._tx_infos: Dict[str, TransactionInfo] = dict()
        self._sig_fetch.connect(self._on_fetch)

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.quit()
        self._thread.wait()

    def get(self, tx_hash: str, request: bool = True) -> TransactionInfo:
        """
        :param tx_hash: transaction hash
        :param request: if True: if info unavailable for tx_hash, try fetch it and if success, emit "fetched" signal
        """
        try:
            return self._tx_infos[tx_hash]
        except KeyError:
            if request:
                self._request(tx_hash)
            raise TxInfoNotFetched(tx_hash)

    def _request(self, tx_hash: str):
        self._sig_fetch.emit(tx_hash)

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_fetch(self, tx_hash: str):
        try:
            _ = self._tx_infos[tx_hash]
        except KeyError:
            pass
        else:
            return

        try:
            self._tx_infos[tx_hash] = self._ctx.ton_client.get_transaction_information(tx_hash)
            tons_logger().info(f'fetched tx info: {tx_hash}')
        except TonError as exception:
            tons_logger().info(f'failed fetch tx_info for {tx_hash} ({type(exception).__name__})')
        else:
            self.fetched.emit(tx_hash)
            return


_tx_info_service: Optional[_TxInfoService] = None


def setup_tx_info_service(ctx: SharedObject):
    global _tx_info_service
    try:
        _tx_info_service.stop()
    except AttributeError:
        pass
    try:
        del _tx_info_service
    except NameError:
        pass

    _tx_info_service = _TxInfoService(ctx)
    _tx_info_service.start()


def stop_tx_info_service():
    global _tx_info_service
    try:
        _tx_info_service.stop()
    except (NameError, AttributeError):
        pass


class TxInfoServiceNotInitialized(GuiException):
    def __init__(self):
        super().__init__("Please run setup_tx_info_service(ctx) first")


def tx_info_service():
    if _tx_info_service is None:
        raise TxInfoServiceNotInitialized
    return _tx_info_service


def transaction_info(tx_hash: str, request: bool = True) -> Optional[TransactionInfo]:
    try:
        return tx_info_service().get(tx_hash, request)
    except TxInfoNotFetched:
        return None


__all__ = ['setup_tx_info_service', 'tx_info_service', 'TxInfoServiceNotInitialized', 'TxInfoNotFetched']
