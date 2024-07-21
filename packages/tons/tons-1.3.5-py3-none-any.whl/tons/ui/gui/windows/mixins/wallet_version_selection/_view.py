from typing import Sequence
from tons.ui.gui.promoted_widgets import RichComboBox


class WalletVersionSelectView:
    _combo_box_version: RichComboBox

    @property
    def version(self) -> str:
        return self._combo_box_version.current_data()

    def set_wallet_versions(self, available_versions: Sequence[str], default_version: str,
                            add_default_version_hint: bool = True):
        combo_box = self._combo_box_version
        available_versions = list(available_versions)
        combo_box.clear()
        for idx, version in enumerate(available_versions):
            hint = '(Default)' if (add_default_version_hint and version == default_version) else ''
            combo_box.add_item(version, hint)

        default_idx = available_versions.index(default_version)
        combo_box.setCurrentIndex(default_idx)


__all__ = ['WalletVersionSelectView']
