from PyQt6.QtGui import QShortcut, QKeySequence

from tons.ui.gui.utils import macos, windows

_MACOS_SEARCH_SHORTCUT = "Ctrl+F"
_MACOS_SEARCH_TOOLTIP = "⌘F"
_LINUX_SEARCH_SHORTCUT = "Ctrl+F"
_LINUX_SEARCH_TOOLTIP = "Ctrl+F"
_WINDOWS_SEARCH_SHORTCUT = "Ctrl+F"
_WINDOWS_SEARCH_TOOLTIP = "Ctrl+F"

_MACOS_HISTORY_SHORTCUT = "Ctrl+Y"
_MACOS_HISTORY_TOOLTIP = "⌘Y"
_LINUX_HISTORY_SHORTCUT = "Ctrl+H"
_LINUX_HISTORY_TOOLTIP = "Ctrl+H"
_WINDOWS_HISTORY_SHORTCUT = "Ctrl+H"
_WINDOWS_HISTORY_TOOLTIP = "Ctrl+H"


def _select_platform_var(macos_var, windows_var, linux_var):
    if macos():
        return macos_var
    elif windows():
        return windows_var
    else:
        return linux_var


class MainWindowViewShortcutsMixin:
    """
    Note: On Mac OS X, the CTRL value corresponds to the Command keys on the Macintosh keyboard,
          and the META value corresponds to the Control keys
    """

    def _setup_shortcuts(self):
        self.search_mode_shortcut = QShortcut(QKeySequence(
            _select_platform_var(_MACOS_SEARCH_SHORTCUT, _WINDOWS_SEARCH_SHORTCUT, _LINUX_SEARCH_SHORTCUT)), self)
        self.search_mode_shortcut.activated.connect(self._enter_search_mode_shortcut)
        self.open_history_window_shortcut = QShortcut(QKeySequence(
            _select_platform_var(_MACOS_HISTORY_SHORTCUT, _WINDOWS_HISTORY_SHORTCUT, _LINUX_HISTORY_SHORTCUT)), self)
        self.open_history_window_shortcut.activated.connect(self._on_open_transactions_history)

        self._update_tooltips()

    def _enter_search_mode_shortcut(self):
        if self._selected_sidebar_item_model is not None:
            self._enter_search_mode()

    def _update_tooltips(self):
        self._button_search.setToolTip(
            f"Search ({_select_platform_var(_MACOS_SEARCH_TOOLTIP, _WINDOWS_SEARCH_TOOLTIP, _LINUX_SEARCH_TOOLTIP)})")
        self._button_show_transaction_history.setToolTip(
            f"Transaction history ({_select_platform_var(_MACOS_HISTORY_TOOLTIP, _WINDOWS_HISTORY_TOOLTIP, _LINUX_HISTORY_TOOLTIP)})")
