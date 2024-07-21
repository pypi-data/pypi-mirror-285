from typing import Dict

from PyQt6.QtWidgets import QWidget

default_stylesheets_memo: Dict[QWidget, str] = dict()


def get_default_stylesheet(widget: QWidget) -> str:
    if widget not in default_stylesheets_memo:
        default_stylesheets_memo[widget] = widget.styleSheet()
    default_stylesheet = default_stylesheets_memo[widget]
    return default_stylesheet


def set_text_display_valid(widget: QWidget, valid: bool):
    try:
        widget.set_text_valid(valid)
        return
    except AttributeError:
        pass
    finally:
        widget.update()

    stylesheet = get_default_stylesheet(widget)
    if not valid:
        stylesheet = merge_stylesheets(stylesheet, "border: 1px solid red")
    widget.setStyleSheet(stylesheet)


def set_text_display_very_valid(widget: QWidget, very_valid: bool):
    try:
        widget.set_text_very_valid(very_valid)
        return
    except AttributeError:
        pass
    finally:
        widget.update()

    stylesheet = get_default_stylesheet(widget)
    if very_valid:
        stylesheet = merge_stylesheets(stylesheet, "border: 1px solid lawngreen")
    widget.setStyleSheet(stylesheet)


def merge_stylesheets(stylesheet1: str, stylesheet2: str) -> str:
    stylesheet1 = stylesheet1.strip().rstrip(';')
    return stylesheet1 + '; ' + stylesheet2


__all__ = ['get_default_stylesheet', 'set_text_display_valid', 'set_text_display_very_valid']
