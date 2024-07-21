import logging
import os
from json import JSONDecodeError

import click
from pydantic.error_wrappers import ValidationError

from tons import settings
from tons.config import Config, ConfigNotFoundError, TonsConfig, ProviderConfig
from tons.logging_ import setup_logging, tons_logger
from tons.tonsdk.utils import setup_default_decimal_context
from tons.utils import storage
from tons.version import __version__
from .._utils import CustomClickException, click_echo_success
from ..._utils import init_shared_object, setup_app, SharedObject


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__)
@click.option("-c", "--config", 'specific_config_path', metavar='', help="Use specific config.yaml file")
@click.option('--debug', is_flag=True, help="Debug mode. Enables logging")
@click.pass_context
def cli(ctx: click.core.Context, specific_config_path: str, debug: bool):
    setup_logging(user_interface='direct', level=logging.DEBUG if debug else None)
    setup_default_decimal_context()
    try:
        ctx.obj = init_shared_object(specific_config_path)

        """Force not to warn if outdated for tons direct"""
        ctx.obj.config.tons.warn_if_outdated = False

        if ctx.invoked_subcommand not in ["config", "init"]:
            setup_app(ctx.obj.config)

    except (FileNotFoundError, JSONDecodeError, ConfigNotFoundError, ValidationError, PermissionError) as e:
        raise CustomClickException(repr(e))


@cli.command()
@click.option('--yes', '-y', 'is_sure', is_flag=True, help='Do not show the prompt')
def init(is_sure):
    """
    Initialize .tons workdir in a current directory
    """
    init_local_workdir = storage.local_config_dir()
    init_local_config_path = os.path.join(init_local_workdir, storage.CONFIG_FILENAME)

    if not is_sure:
        click.confirm(f"This will initialize a tons working directory in {init_local_workdir}\nAre you sure?",
                      abort=True)

    tons = TonsConfig(workdir=init_local_workdir)  #
    provider = ProviderConfig()                    # TODO is this unnecessary?
    config = Config(tons=tons, provider=provider)  #
    setup_app(config)
    storage.save_yaml(init_local_config_path, config.dict())

    click_echo_success(f'Local config {init_local_config_path} has been initialized.')
