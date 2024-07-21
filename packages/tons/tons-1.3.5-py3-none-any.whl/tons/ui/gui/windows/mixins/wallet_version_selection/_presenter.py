from typing import Protocol, Sequence, Optional


class Model(Protocol):
    @property
    def available_wallet_versions(self) -> Sequence[str]: ...
    @property
    def default_wallet_version(self) -> str: ...


class View(Protocol):
    def set_wallet_versions(self, available_versions: Sequence[str], default_version: str,
                            add_default_version_hint: bool = True): ...


class WalletVersionSelectPresenter:
    _model: Model
    _view: View

    def _display_versions(self, default_version: Optional[str] = None, add_default_version_hint: bool = True):
        available_versions = self._model.available_wallet_versions
        default_version = default_version or self._model.default_wallet_version
        self._view.set_wallet_versions(available_versions, default_version,
                                       add_default_version_hint=add_default_version_hint)


__all__ = ['WalletVersionSelectPresenter']
