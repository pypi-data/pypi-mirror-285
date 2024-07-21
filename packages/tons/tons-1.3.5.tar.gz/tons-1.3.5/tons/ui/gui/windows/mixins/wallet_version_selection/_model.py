from typing import Tuple

from tons.config import Config
from tons.ui.gui.utils import available_wallet_versions


class WalletVersionSelectModel:
    _config: Config

    @property
    def available_wallet_versions(self) -> Tuple[str, ...]:
        return available_wallet_versions()

    @property
    def default_wallet_version(self) -> str:
        try:
            result = self._config.tons.default_wallet_version.value
        except AttributeError:
            result = self._config.tons.default_wallet_version
        return result


__all__ = ['WalletVersionSelectModel']
