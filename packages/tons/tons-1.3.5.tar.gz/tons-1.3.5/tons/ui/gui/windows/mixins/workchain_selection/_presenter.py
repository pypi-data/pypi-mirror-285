from typing import Protocol, Sequence, Optional, Any


class Model(Protocol):
    @property
    def available_workchains(self) -> Sequence[int]: ...
    @property
    def available_workchains_hints(self) -> Sequence[int]: ...
    @property
    def default_workchain(self) -> int: ...


class View(Protocol):
    def set_workchains(self, available_workchains: Sequence[int],
                       default_workchain: int,
                       hints: Optional[Sequence[Any]] = None): ...


class WorkchainSelectPresenter:
    _model: Model
    _view: View

    def _display_workchains(self):
        available_workchains = self._model.available_workchains
        available_workchains_hints = self._model.available_workchains_hints
        default_workchain = self._model.default_workchain
        self._view.set_workchains(available_workchains, default_workchain, available_workchains_hints)


__all__ = ['WorkchainSelectPresenter']
