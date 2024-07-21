from functools import lru_cache


@lru_cache
def top_padding() -> int:
    return 8


@lru_cache
def bottom_padding() -> int:
    return top_padding()


@lru_cache()
def left_padding() -> int:
    return 24 - 7


@lru_cache
def right_padding() -> int:
    return left_padding()


@lru_cache
def horizontal_spacing() -> int:
    return 9


@lru_cache
def icon_width() -> int:
    return 16


@lru_cache
def icon_height() -> int:
    return 16


@lru_cache
def icon_top_padding() -> int:
    return 3


@lru_cache
def button_icon_width() -> int:
    return 16


@lru_cache
def button_icon_height() -> int:
    return 16


@lru_cache
def button_horizontal_margin() -> int:
    return 7


@lru_cache
def button_horizontal_spacing() -> int:
    return 7


@lru_cache
def button_vertical_margin() -> int:
    return 5


@lru_cache
def button_height() -> int:
    return 30


@lru_cache
def selection_rectangle_radius() -> int:
    return 5


@lru_cache
def dash_rice_relative_width() -> float:
    return 0.4


@lru_cache
def dash_loader_relative_height() -> float:
    return 0.1


@lru_cache
def dash_loader_relative_shift() -> float:
    return 0.1


@lru_cache
class TransactionDistances:
    top_padding = top_padding()
    bottom_padding = bottom_padding()
    left_padding = left_padding()
    right_padding = right_padding()

    horizontal_spacing = horizontal_spacing()

    icon_width = icon_width()
    icon_height = icon_height()

    icon_top_padding = icon_top_padding()

    button_icon_width = button_icon_width()
    button_icon_height = button_icon_height()
    button_horizontal_margin = button_horizontal_margin()
    button_horizontal_spacing = button_horizontal_spacing()
    button_vertical_margin = button_vertical_margin()
    button_height = button_height()

    selection_rectangle_radius = selection_rectangle_radius()

    dash_rice_relative_width = dash_rice_relative_width()
    dash_loader_relative_height = dash_loader_relative_height()
    dash_loader_relative_shift = dash_loader_relative_shift()

