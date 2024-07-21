from typing import Protocol


class Model(Protocol):
    def setup_dns_info_signals(self, presenter: 'DnsInfoServicePresenter'): ...


class DnsInfoServicePresenter:
    _model: Model

    def init_dns_info_service(self):
        self._model.setup_dns_info_signals(self)


__all__ = ['DnsInfoServicePresenter']
