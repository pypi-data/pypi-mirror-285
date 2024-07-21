import typing as t
from tons.ui.interactive_cli._sets._base import MenuItem
from ..._modified_inquirer import terminal


def add_menu_item(ord_dict: t.OrderedDict, title: str, hotkey: t.Optional[str], callback: t.Callable):
    if hotkey:
        title = _get_formatted_title(title, hotkey)
    ord_dict[title] = MenuItem(callback, hotkey)


def _get_formatted_title(title: str, hotkey: str) -> str:
    assert hotkey.lower() == hotkey and len(hotkey) == 1
    hotkey_idx = title.lower().find(hotkey)
    assert hotkey_idx >= 0
    formatted_title = title[:hotkey_idx]
    formatted_title += terminal.underline + title[hotkey_idx] + terminal.no_underline
    formatted_title += title[hotkey_idx + 1:]
    return formatted_title