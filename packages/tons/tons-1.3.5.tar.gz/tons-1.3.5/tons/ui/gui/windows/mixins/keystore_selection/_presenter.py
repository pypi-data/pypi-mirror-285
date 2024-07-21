from typing import Protocol, List, Sequence


class Model(Protocol):
    @property
    def keystores_names(self) -> List[str]: ...
    @property
    def keystore_name(self) -> str: ...


class View(Protocol):
    def set_keystores_names(self, names: Sequence[str], current_idx: int): ...


class KeystoreSelectPresenter:
    _model: Model
    _view: View

    def _display_keystores(self):
        keystores_names = self._model.keystores_names
        current_idx = keystores_names.index(self._model.keystore_name)
        keystores_names[0], keystores_names[current_idx] = keystores_names[current_idx], keystores_names[0]
        self._view.set_keystores_names(keystores_names, 0)


__all__ = ['KeystoreSelectPresenter']