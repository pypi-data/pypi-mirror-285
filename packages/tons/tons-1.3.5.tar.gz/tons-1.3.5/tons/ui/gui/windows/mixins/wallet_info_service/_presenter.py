from typing import Protocol


class Model(Protocol):
    def setup_wallet_info_signals(self, presenter: 'WalletInfoServicePresenter'): ...


class WalletInfoServicePresenter:
    _model: Model

    def init_wallet_info_service(self):
        self._model.setup_wallet_info_signals(self)


__all__ = ['WalletInfoServicePresenter']
