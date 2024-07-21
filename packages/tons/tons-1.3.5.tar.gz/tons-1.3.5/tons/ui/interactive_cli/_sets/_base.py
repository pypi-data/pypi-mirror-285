import sys
from abc import ABCMeta, abstractmethod
from typing import Optional, OrderedDict as OrderedDictTyping
from uuid import UUID

import inquirer
from smartcard.Exceptions import CardConnectionException

from tons.tonclient import TonError
from .._exceptions import EscButtonPressed, InvalidUsageError
from .._modified_inquirer import ModifiedPrompt, MenuWithHotkeys
from .._utils import echo_error, echo_success, processing
from .._validators import non_empty_string
from .._background import BackgroundTaskCritical
from ..._utils import SharedObject, truncate


class MenuItem:
    def __init__(self, callback, hotkey):
        self.callback = callback
        self.hotkey = hotkey


class BaseSet(ModifiedPrompt, metaclass=ABCMeta):
    MENU_KEY = "menu_option"

    def __init__(self, ctx: SharedObject) -> None:
        self.ctx = ctx
        self._menu_message = "Pick command"
        self._exit = False

    @property
    def starting_menu_pos(self):
        return 0

    def show(self):
        while not self._exit:
            handlers = self._handlers()
            items = [
                MenuWithHotkeys(self.MENU_KEY, message=self._menu_message,
                                choices=handlers.keys(),
                                hotkeys=[handler.hotkey for handler in handlers.values()],
                                carousel=True,
                                starting_pos=self.starting_menu_pos),
            ]

            try:
                item = self._prompt(items)[self.MENU_KEY]
            except (EscButtonPressed, KeyboardInterrupt):
                self._handle_exit()
                continue
            except Exception as e:
                if self.ctx.debug_mode:
                    raise
                echo_error(f"Unexpected UI error: {e.__repr__()}")
                break

            try:
                self._handlers()[item].callback()
            except (EscButtonPressed, KeyboardInterrupt):
                pass
            except CardConnectionException:
                echo_error(
                    'Keystore is locked due to lost yubikey connection. Please, re-enter keystore.')
            except BackgroundTaskCritical as e:
                echo_error(e.__repr__())
                sys.exit(2)
            except Exception as e:
                if self.ctx.debug_mode:
                    raise

                echo_error(e.__repr__())

    @abstractmethod
    def _handlers(self) -> OrderedDictTyping[str, MenuItem]:
        raise NotImplementedError

    def _handle_exit(self):
        self._exit = True

    def _select_whitelist_available_name(self, whitelist, old_name: str) -> Optional[str]:
        while True:
            new_contact_name = self._prompt([
                inquirer.Text(
                    "new_contact_name",
                    message='Enter new name',
                    default=old_name,
                    validate=non_empty_string
                ),
            ])["new_contact_name"]
            if new_contact_name == old_name:
                return None
            elif whitelist.get_contact(new_contact_name) is not None:
                echo_error(f"Contact with the name {new_contact_name} already exists")
            else:
                return new_contact_name

    def _select_wallet_available_name(self, old_name: str) -> Optional[str]:
        if not hasattr(self, 'ctx') or not hasattr(self.ctx, 'keystore'):
            raise InvalidUsageError

        while True:
            new_wallet_name = self._prompt([
                inquirer.Text(
                    "new_wallet_name",
                    message='Enter new name',
                    default=old_name,
                    validate=non_empty_string),
            ])["new_wallet_name"]
            if new_wallet_name == old_name:
                return old_name

            elif self.ctx.keystore.get_record_by_name(new_wallet_name) is not None:
                echo_error(f"Wallet with the name {new_wallet_name} already exists")
                return None

            else:
                return new_wallet_name

    def _wait_for_result_and_echo(self, task_id: UUID):
        with processing():
            while (task := self.ctx.background_task_manager.get_task(task_id)).is_pending:
                pass

        result = str(task.result.broadcast_result)

        if isinstance(task.result.broadcast_result, TonError):
            if not self.ctx.debug_mode:
                result = truncate(result)
            echo_error(result)
        else:
            echo_success(result)
