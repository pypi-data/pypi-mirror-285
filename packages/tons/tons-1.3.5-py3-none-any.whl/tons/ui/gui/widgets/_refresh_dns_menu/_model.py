from tons.config import Config


class RefreshDnsMenuModel:
    def __init__(self, config: Config):
        self._max_expiring_in = config.dns.max_expiring_in

    @property
    def max_expiring_in(self) -> int:
        return self._max_expiring_in
