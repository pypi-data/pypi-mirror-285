import contextlib
from typing import Sequence, List

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox

from tons.ui.gui.utils import slot_exc_handler, adjust_size_independently, suppress_combo_index_change, get_icon


class KeystoreSelectView:
    _keystore_changed = pyqtSignal(str)
    _combo_box_keystore: QComboBox

    def init_keystore_select_view(self):
        self._different_keystore_selected = False
        self.__setup_signals()

    def __setup_signals(self):
        self._combo_box_keystore.currentIndexChanged.connect(self._on_combo_box_index_changed)

    @slot_exc_handler()
    def _on_combo_box_index_changed(self, current_index: int):
        with self.suppress_combo_box_index_change_signal():
            adjust_size_independently(self._combo_box_keystore)
        self._different_keystore_selected = current_index != 0
        self._keystore_changed.emit(self.get_keystore_name_by_index(current_index))

    def set_keystores_names(self, names: Sequence[str], current_idx: int):
        with self.suppress_combo_box_index_change_signal():
            combo_box = self._combo_box_keystore
            combo_box.clear()
            icon = get_icon('lock-solid.svg')
            for name in names:
                combo_box.addItem(icon, name)
            combo_box.setCurrentIndex(current_idx)
        self._on_combo_box_index_changed(current_idx)

    def get_keystores_names(self) -> List[str]:
        combo_box = self._combo_box_keystore
        return [combo_box.itemText(i) for i in range(combo_box.count())]

    def get_keystore_name_by_index(self, idx: int):
        combo_box = self._combo_box_keystore
        return combo_box.itemText(idx)

    @property
    def current_keystore_name(self) -> str:
        return self._combo_box_keystore.currentText()

    @property
    def different_keystore_is_selected(self) -> bool:
        return self._different_keystore_selected

    @contextlib.contextmanager
    def suppress_combo_box_index_change_signal(self):
        with suppress_combo_index_change(self._combo_box_keystore, [self._on_combo_box_index_changed]):
            yield


__all__ = ['KeystoreSelectView']