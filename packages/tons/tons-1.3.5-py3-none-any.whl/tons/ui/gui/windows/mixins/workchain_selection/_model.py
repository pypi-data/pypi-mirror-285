from typing import Tuple

from tons.ui.gui.utils import available_workchains, available_workchains_hints


class WorkchainSelectModel:
    @property
    def available_workchains(self) -> Tuple[int, ...]:
        return available_workchains()

    @property
    def available_workchains_hints(self) -> Tuple[str, ...]:
        return available_workchains_hints()

    @property
    def default_workchain(self) -> int:
        return 0


__all__ = ['WorkchainSelectModel']
