from tons.logging_ import setup_logging, tons_logger
from ._commands import _config_cmd  # noqa: F401
from ._commands import _contract_cmd  # noqa: F401
from ._commands import _dev_cmd  # noqa: F401
from ._commands import _dns_cmd  # noqa: F401
from ._commands import _keystore_cmd  # noqa: F401
# from ._commands import _tonconnect  # noqa: F401
from ._commands import _wallet_cmd  # noqa: F401
from ._commands import _whitelist_cmd  # noqa: F401
from ._commands import _multisig
from ._commands._base_cmd import cli


def main():
    cli()


if __name__ == '__main__':
    main()
