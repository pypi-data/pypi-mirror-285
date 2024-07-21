from functools import wraps
from typing import Callable, Any

from tons.logging_ import tons_logger


def slot_exc_handler(arg=None, *, catch=Exception):
    """
    A decorator to handle exceptions in PyQt slots.

    This decorator should be applied to every `pyqtSlot` to ensure proper exception handling.
    The problem is described here:
    https://stackoverflow.com/questions/18740884/preventing-pyqt-to-silence-exceptions-occurring-in-slots

    The solutions mentioned in the answers did not work well with QThreads and resulted in a frozen UI.
    Therefore, this separate decorator is implemented to address this issue.

    Args:
        catch (Exception, optional): The type of exception to catch. Defaults to Exception.

    Returns:
        Callable: A decorated function that handles exceptions in PyQt slots.
    """
    def magic(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except catch as e:
                msg = f"In pyqtSlot '{wrapper.__name__}' caught: {type(e).__name__}\n"
                tons_logger().error(msg, exc_info=e)
        return wrapper

    if callable(arg):
        return magic(arg)

    return magic


def qt_exc_handler(method: Callable):
    """
    Prevents app from crashing because of unhandled exceptions
    Should be applied to overloaded Qt methods that are called from the Qt event loop
    """
    @wraps(method)
    def magic(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            tons_logger().warn(f"Unexpected error in '{type(self).__name__}.{method.__name__}(..)'", exc_info=e)

            super_instance = super(type(self), self)
            super_method = getattr(super_instance, method.__name__)
            super_result = super_method(*args, **kwargs)

            return super_result

    return magic
