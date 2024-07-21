from typing import Optional, Sequence, Any

from PyQt6.QtWidgets import QComboBox

from tons.ui.gui.promoted_widgets import RichComboBox


class WorkchainSelectView:
    _combo_box_workchain: RichComboBox

    @property
    def workchain(self) -> int:
        return int(self._combo_box_workchain.current_data())

    def set_workchains(self, available_workchains: Sequence[int],
                       default_workchain: int,
                       hints: Optional[Sequence[Any]] = None):
        combo_box = self._combo_box_workchain
        values = list(available_workchains)
        combo_box.clear()

        for idx, value in enumerate(values):
            data = str(value)
            hint = hints[idx] if hints is not None else ''
            combo_box.add_item(data, hint)

        default_idx = values.index(default_workchain)
        combo_box.setCurrentIndex(default_idx)


__all__ = ['WorkchainSelectView']
