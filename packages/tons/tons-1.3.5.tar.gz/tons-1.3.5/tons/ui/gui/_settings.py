import os
import sys
from pathlib import Path

from tons.settings import TONS_IS_BUNDLE


def _correct_path(dev_location: str, pyinstaller_location: str) -> str:
    # https://pyinstaller.org/en/stable/runtime-information.html
    if TONS_IS_BUNDLE:
        return os.path.join(sys._MEIPASS, pyinstaller_location)
    else:
        return dev_location


TONS_GUI_FONTS_DIR = _correct_path("tons/ui/gui/uis/_qt_assets/fonts/", "tons_assets/fonts/")
TONS_GUI_LIGHT_ICONS_DIR = Path(_correct_path('tons/ui/gui/uis/_qt_assets/icons/light/', "tons_assets/icons/light"))
TONS_GUI_DARK_ICONS_DIR = Path(_correct_path('tons/ui/gui/uis/_qt_assets/icons/dark/', "tons_assets/icons/dark"))
TONS_GUI_NOTIFICATION_ICO = _correct_path("devtools/distribute/assets/tons-interactive.ico",
                                          "tons_assets/tons-interactive.ico")
