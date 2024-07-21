import decimal
from copy import deepcopy

from tons import settings
from tons.config import Config, TonNetworkEnum, TonScannerEnum
from tons.tonsdk.contract.wallet import WalletVersionEnum
from tons.ui.gui.utils import xstr
from tons.ui.gui.windows.mixins.wallet_version_selection import WalletVersionSelectModel
from tons.utils import storage


class PreferencesModel(WalletVersionSelectModel):
    def __init__(self, config: Config):
        self._config = config

    def save(self, *, user_directory, api_key, version, network, testnet_api_key, dns_expiring_in, dns_refresh_amount,
             jetton_gas_amount, scanner):
        config = deepcopy(self._config)
        config.tons.workdir = user_directory
        config.provider.dapp.api_key = api_key
        config.tons.default_wallet_version = WalletVersionEnum(version)
        config.provider.dapp.network = TonNetworkEnum(network)
        config.provider.dapp.testnet_api_key = testnet_api_key
        config.dns.max_expiring_in = int(dns_expiring_in)
        config.dns.refresh_send_amount = decimal.Decimal(dns_refresh_amount)
        config.jetton.gas_amount = decimal.Decimal(jetton_gas_amount)
        config.gui.scanner = scanner
        config_path = settings.current_config_path()
        config_dict = config.dict(exclude_unset=False)
        storage.save_yaml(config_path, config_dict)

    @classmethod
    def get_default_config_model(cls) -> 'PreferencesModel':
        return cls(Config())

    @property
    def user_directory(self) -> str:
        return self._config.tons.workdir

    @property
    def version(self):
        return self.default_wallet_version

    @property
    def api_key(self) -> str:
        return xstr(self._config.provider.dapp.__dict__['api_key'])

    @property
    def testnet_api_key(self) -> str:
        return xstr(self._config.provider.dapp.testnet_api_key)

    @property
    def network(self) -> TonNetworkEnum:
        return self._config.provider.dapp.network

    @property
    def scanner(self) -> TonScannerEnum:
        return self._config.gui.scanner

    @property
    def dns_expiring_in(self) -> int:
        return self._config.dns.max_expiring_in

    @property
    def dns_refresh_amount(self) -> decimal.Decimal:
        return self._config.dns.refresh_send_amount

    @property
    def jetton_gas_amount(self) -> decimal.Decimal:
        return self._config.jetton.gas_amount


