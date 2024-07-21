import logging
import os
import sys
from json import JSONDecodeError

from pydantic import ValidationError

from tons.config import ConfigNotFoundError
from tons.logging_ import setup_logging
from tons.tonsdk.utils import setup_default_decimal_context
from tons.ui.interactive_cli._background import BackgroundTaskManager
from tons.ui._utils import init_shared_object, setup_app
from tons.ui.interactive_cli._exceptions import EscButtonPressed
from tons.ui.interactive_cli._sets import EntrypointSet
from tons.ui.interactive_cli._utils import echo_error, echo_success


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--debug":
        debug_mode = True
    else:
        debug_mode = False

    os.system('cls' if os.name == 'nt' else 'clear')

    setup_logging('interactive', logging.DEBUG if debug_mode else None)

    setup_default_decimal_context()

    try:
        context = init_shared_object()
        setup_app(context.config)

    except (FileNotFoundError, JSONDecodeError, ConfigNotFoundError, ValidationError, PermissionError) as e:
        echo_error(e)
        return

    context.debug_mode = debug_mode

    context.ton_daemon.start()

    context.background_task_manager = BackgroundTaskManager(context)
    context.background_task_manager.start()

    workdir_abspath = os.path.abspath(context.config.tons.workdir)
    echo_success(f"Current working directory: {workdir_abspath}")

    try:
        EntrypointSet(context).show()
    except (EscButtonPressed, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    main()
