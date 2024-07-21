import weakref
from decimal import Decimal
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot

from tons.logging_ import tons_logger
from tons.tonclient import TonError
from tons.ui._utils import SharedObject
from tons.ui.gui.exceptions import GuiException, CtxReferenceError
from tons.ui.gui.utils import slot_exc_handler


class _FiatPriceService(QObject):
    UPDATE_INTERVAL_MS = 5000

    fetched = pyqtSignal()

    def __init__(self, ctx: SharedObject):
        super().__init__()
        self.__ctx = weakref.ref(ctx)

        self._thread = QThread()
        self._thread.setObjectName('fiat service thread')
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run)

        self._timer = self._setup_timer()

        self._price_usd: Optional[Decimal] = None

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    def _setup_timer(self) -> QTimer:
        timer = QTimer()
        timer.setInterval(self.UPDATE_INTERVAL_MS)
        timer.timeout.connect(self.update)
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

    def update_now(self):
        self._timer.timeout.emit()

    @pyqtSlot()
    @slot_exc_handler()
    def update(self):
        try:
            self._price_usd = self._ctx.ton_client.get_ton_price_usd()
            tons_logger().debug(f'ton price fetched: {self._price_usd}')
        except CtxReferenceError:
            tons_logger().info(f'failed fetch price usd (ctx ref error)')
        except TonError as exception:
            tons_logger().info(f'failed fetch price usd ({type(exception).__name__})')
        else:
            self.fetched.emit()

    @property
    def price_usd(self) -> Optional[Decimal]:
        return self._price_usd


_fiat_price_service: Optional[_FiatPriceService] = None


def setup_fiat_price_service(ctx: SharedObject):
    global _fiat_price_service
    try:
        _fiat_price_service.stop()
    except AttributeError:
        pass
    try:
        del _fiat_price_service
    except NameError:
        pass

    _fiat_price_service = _FiatPriceService(ctx)
    _fiat_price_service.start()


def stop_fiat_price_service():
    global _fiat_price_service
    try:
        _fiat_price_service.stop()
    except (NameError, AttributeError):
        pass


class FiatPriceServiceNotInitialized(GuiException):
    def __init__(self):
        super().__init__("Please run setup_fiat_price_service(ctx) first")


def fiat_price_service():
    if _fiat_price_service is None:
        raise FiatPriceServiceNotInitialized
    return _fiat_price_service


def ton_usd_price() -> Optional[Decimal]:
    return _fiat_price_service.price_usd


__all__ = ['setup_fiat_price_service', 'fiat_price_service', 'FiatPriceServiceNotInitialized', 'ton_usd_price']
