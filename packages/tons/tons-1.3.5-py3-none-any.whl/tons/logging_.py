import logging
import logging.handlers
import os
import platform
import re
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Tuple, List

from tons.tonsdk.crypto.bip39 import _english

_logger_set_up = False

_filename = 'log.txt'
_backup_count = 10
_max_file_size_kb = 512

_logger_name = 'tons'
_app_dir = 'tons'
_log_dir = 'log'
_env_var = 'TONS_LOG_DIRECTORY'

_columns = ['[%(name)s]', '[{interface}]', '%(asctime)s', '%(threadName)s', '(%(thread)d)', '%(levelname)s', '%(message)s']
_separator = '\t'  # group separator
_escaped_separator = '\\t'

_dont_log_at_all = logging.CRITICAL + 1
_default_level = _dont_log_at_all
_minimal_qt_stream_level = logging.WARNING
_minimal_qt_file_level = logging.INFO


class UserInterface(str, Enum):
    direct = 'direct'
    interactive = 'interactive'
    qt = 'qt'
    tests = 'tests'


class SensitiveFormatter(logging.Formatter):
    _mnemonic_words_threshold = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mnemonic_words = set(_english.words)

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        return self._filter(formatted)

    def _filter(self, txt: str) -> str:
        txt = self._filter_mnemonic_words(txt)
        return txt

    def _filter_mnemonic_words(self, text: str) -> str:
        words = [(match.span(), match.group()) for match in re.finditer('[a-z]+', text)]
        result, prev_end = '', 0
        for match in re.finditer('1{%d,}' % self._mnemonic_words_threshold,
                                 ''.join([str(int(word in self._mnemonic_words)) for (_, _), word in words])):
            for (begin, end), word in words[match.span()[0]:match.span()[1]]:
                result += text[prev_end:begin] + '*' * (end - begin)
                prev_end = end
        result += text[prev_end:]
        return result


def _escape_separator(message: str) -> str:
    return message.replace(_separator, _escaped_separator)


def _ensure_empty_line_at_end_for_multiline(message: str) -> str:
    if '\n' in message:
        message = message.rstrip('\n') + '\n\n'
    return message


class TonsFormatter(SensitiveFormatter):
    def format(self, record: logging.LogRecord) -> str:
        try:
            message = record.msg
        except AttributeError:
            pass
        else:
            message = _escape_separator(message)
            record.msg = message

        result = super().format(record)
        result = _ensure_empty_line_at_end_for_multiline(result)

        return result


def _get_stream_handler(user_interface: UserInterface, level: int):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    if user_interface != UserInterface.qt:
        handler.setLevel(_dont_log_at_all)
    else:
        handler.setLevel(min(level, _minimal_qt_stream_level))
    return handler


def _get_file_handler(user_interface: UserInterface, level: int):
    directory = _get_log_directory()
    os.makedirs(directory, exist_ok=True)
    path = directory / _filename
    handler = logging.handlers.RotatingFileHandler(filename=path,
                                                   maxBytes=_max_file_size_kb * 1024,
                                                   backupCount=_backup_count)
    if user_interface != UserInterface.qt:
        handler.setLevel(level)
    else:
        handler.setLevel(min(level, _minimal_qt_file_level))
    return handler


def _get_formatter(user_interface: UserInterface) -> logging.Formatter:
    format_ = _separator.join(_columns)
    format_ = format_.format(interface=user_interface.value)
    return TonsFormatter(format_)


def _get_log_directory() -> Path:
    return _get_env_log_directory() or _get_default_log_directory()


def _get_env_log_directory() -> Optional[Path]:
    directory = os.getenv(_env_var)
    if directory is None:
        return None
    return Path(directory)


def _get_default_log_directory() -> Path:
    platform_name = platform.system().lower()
    if platform_name == 'windows':
        base = os.path.expanduser('~/.config/')
        return Path(base) / _app_dir / _log_dir
    elif platform_name == 'linux':
        base = os.path.expanduser('~/.config/')
        return Path(base) / _app_dir / _log_dir
    elif platform_name == 'darwin':
        base = os.path.expanduser('~/Library/Logs/tons')
        return Path(base) / _log_dir
    else:
        raise NotImplementedError(f"Logging is not supported for {platform_name}")


def _file_logging_enabled(logger: logging.Logger) -> bool:
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.level <= logging.CRITICAL:
            return True
    return False


def _setup_handlers(logger: logging.Logger, user_interface: UserInterface, level: int):
    stream_handler = _get_stream_handler(user_interface, level)
    file_handler = _get_file_handler(user_interface, level)

    formatter = _get_formatter(user_interface)

    logger.handlers.clear()
    if user_interface != UserInterface.tests:
        for handler in [stream_handler, file_handler]:
            handler.setFormatter(formatter)
            logger.addHandler(handler)


def setup_logging(user_interface: Union[str, UserInterface], level: Optional[int] = None):
    global _logger_set_up

    if level is None:
        level = _default_level

    user_interface = UserInterface(user_interface)

    logger = logging.getLogger(_logger_name)

    _setup_handlers(logger, user_interface, level)

    logger.setLevel(logging.DEBUG)  # desired level is specified on the handlers level

    if _file_logging_enabled(logger):
        print(f'[!] Logs saved to {_get_log_directory()}')

    _logger_set_up = True


class LoggerNotSetup(Exception):
    def __init__(self):
        super().__init__("setup_logging(..) has not been called. Please setup the logging first")


def tons_logger():
    if not _logger_set_up:
        raise LoggerNotSetup
    return logging.getLogger(_logger_name)


__all__ = ['tons_logger', 'setup_logging']
