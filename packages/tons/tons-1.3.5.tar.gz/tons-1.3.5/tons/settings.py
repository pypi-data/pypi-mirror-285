import os
import sys
from typing import Optional

from tons.utils import storage

# config
GLOBAL_CONFIG_PATH: str = storage.get_global_config_path()
CUSTOM_CONFIG_PATH: Optional[str] = storage.get_custom_config_path()


def current_config_path():
    return CUSTOM_CONFIG_PATH or GLOBAL_CONFIG_PATH


# dapp
DAPP_MAINNET_GRAPHQL_URL = "https://dapp-01.tontech.io/graphql"
DAPP_MAINNET_BROADCAST_URL = "https://dapp-01.tontech.io/broadcast"
DAPP_TESTNET_GRAPHQL_URL = "https://dapp-test.tontech.io/graphql"
DAPP_TESTNET_BROADCAST_URL = "https://dapp-test.tontech.io/broadcast"
DAPP_RECORDS_LIMIT = 50

# dns
DNS_MAINNET_COLLECTION_ADDRESS = 'EQC3dNlesgVD8YbAazcauIrXBPfiVhMMr5YYk2in0Mtsz0Bz'
DNS_TESTNET_COLLECTION_ADDRESS = 'EQDjPtM6QusgMgWfl9kMcG-EALslbTITnKcH8VZK1pnH3UZA'

# tons
KEYSTORE_PASSWORD = os.environ.get('TONS_KEYSTORE_PASSWORD', '')
YUBIKEY_PIN = os.environ.get('TONS_YUBIKEY_PIN', '')
PYPI_PACKAGE_URL = "https://pypi.python.org/pypi/tons/json"

# keystore
CURRENT_KEYSTORE_VERSION = 6

# tonconnect
BRIDGE_URL = "https://bridge.tonapi.io"
BRIDGE_HOST = "bridge.tonapi.io"
BRIDGE_PORT = 443
BRIDGE_WAIT_NEW_REQUEST_SEC = 10

# jetton
KNOWN_JETTONS_URL = 'https://raw.githubusercontent.com/tonkeeper/ton-assets/main/jettons.json'

# pyinstaller
TONS_IS_BUNDLE = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Documentation
DOCUMENTATION_LINK = "https://tonfactory.github.io/tons-docs/"
SUPPORT_LINK = "https://t.me/tonfactorychat/"
DOCUMENTATION_SHORTCUTS_LINK = "https://tonfactory.github.io/tons-docs/shortcuts"

KEYSTORE_FILE_EXT = '.keystore'
