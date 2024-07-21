import contextlib
from typing import Optional

import click

from tons.ui._utils import SharedObject, get_ton_client, get_ton_daemon
from tons.utils.spinner import Spinner


def echo_error(msg: str, only_cross=False):
    _msg = "\x1b(B\x1b[m[\x1b[33m✕\x1b(B\x1b[m] "
    if not only_cross:
        _msg += "{error}: ".format(error=click.style('Error', fg='red'))
    _msg += str(msg)

    click.echo(_msg)


def echo_success(msg: Optional[str] = None, only_msg=False):
    if msg is None:
        msg = "Done"

    if not only_msg:
        msg = "\x1b(B\x1b[m[\x1b[33m✓\x1b(B\x1b[m] " + str(msg)

    click.echo(msg)


def echo_warning(msg: str):
    click.echo("\x1b(B\x1b[m \x1b[33m⚠\x1b(B\x1b[m  " + str(msg))


@contextlib.contextmanager
def processing(spinner_message: str = 'wait'):
    spinner = Spinner(spinner_message)
    try:
        spinner.start()
        yield
    finally:
        spinner.stop()


def reinit_client_and_daemons(ctx: SharedObject):
    ctx.ton_client = get_ton_client(ctx.config)
    ctx.ton_daemon.stop()
    ctx.ton_daemon = get_ton_daemon(ctx.config, ctx.ton_client)
    ctx.ton_daemon.start()
    ctx.background_task_manager.start()


