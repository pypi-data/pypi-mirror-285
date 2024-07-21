import contextlib
from typing import Sequence

from PyQt6.QtCore import pyqtSignal, Qt, QObject
from PyQt6.QtWidgets import QComboBox

from tons.ui.gui.exceptions import GuiException
from tons.ui.gui.utils import ContactLocation, GlobalWhitelistLocation, LocalWhitelistLocation, slot_exc_handler, \
    adjust_size_independently, suppress_combo_index_change, get_icon


class WhitelistsViewComponent(QObject):
    changed = pyqtSignal(ContactLocation)

    def __init__(self, combo_box: QComboBox):
        super().__init__()
        self._combo_box = combo_box
        self._setup_signals()

    def _setup_signals(self):
        self._combo_box.currentIndexChanged.connect(self._on_combo_box_index_changed)

    def set_locations(self, locations: Sequence[ContactLocation], current_idx: int = 0):
        with self.suppress_combo_box_index_change_signal():
            combo_box = self._combo_box
            combo_box.clear()

            for idx, location in enumerate(locations):
                name = self.get_pretty_name(location)
                icon = self.get_icon(location)
                combo_box.addItem(icon, name)
                combo_box.setItemData(idx, location)

            combo_box.setCurrentIndex(current_idx)
        self._on_combo_box_index_changed(current_idx)

    def set_location(self, location: ContactLocation):
        combo_box = self._combo_box
        for idx in range(combo_box.count()):
            item_location = combo_box.itemData(idx)
            if item_location == location:
                combo_box.setCurrentIndex(idx)
                return
        raise LocationNotFound(location)

    @property
    def selected_location(self) -> ContactLocation:
        idx = self._combo_box.currentIndex()
        location = self._combo_box.itemData(idx)
        return location

    @staticmethod
    def get_pretty_name(location: ContactLocation) -> str:
        if isinstance(location, GlobalWhitelistLocation):
            return 'Global whitelist'
        elif isinstance(location, LocalWhitelistLocation):
            return location.keystore_name
        else:
            raise NotImplementedError('Unknown whitelist sort')

    @staticmethod
    def get_icon(location: ContactLocation):
        return get_icon(WhitelistsViewComponent.get_icon_path(location))

    @staticmethod
    def get_icon_path(location: ContactLocation):
        if isinstance(location, GlobalWhitelistLocation):
            return 'contact-global.svg'
        elif isinstance(location, LocalWhitelistLocation):
            return 'contact-local.svg'
        else:
            raise NotImplementedError('Unknown whitelist sort')

    @contextlib.contextmanager
    def suppress_combo_box_index_change_signal(self):
        with suppress_combo_index_change(self._combo_box, [self._on_combo_box_index_changed]):
            yield

    @slot_exc_handler()
    def _on_combo_box_index_changed(self, current_index: int):
        with self.suppress_combo_box_index_change_signal():
            adjust_size_independently(self._combo_box)
        contact_location = self._combo_box.itemData(current_index, Qt.ItemDataRole.UserRole)
        self.changed.emit(contact_location)


class LocationNotFound(GuiException):
    def __init__(self, location: ContactLocation):
        super().__init__(f'Location not found: {location}')
        self.location = location