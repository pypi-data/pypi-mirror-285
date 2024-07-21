from functools import lru_cache

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont

from tons.ui.gui.utils import text_pixel_width, text_pixel_size
from .._fonts import TransactionFonts, top_height, bottom_height
from tons.ui.gui.widgets._transaction_list_item._model_getters import get_state_text, get_time, get_start_time, \
    get_end_time, get_dash
from ._sizes import TransactionDistances
from ._text_constants import cancel_button_text, get_button_text
from .._item_data import TransactionListItemData


@lru_cache(maxsize=1024)
def _text_pixel_width(text: str, font: QFont) -> int:
    return int(text_pixel_width(text, font) + 1)


@lru_cache(maxsize=1024)
def _text_pixel_height(text: str, font: QFont) -> int:
    return int(text_pixel_size(text, font).height() + 1)


class TransactionRectangles:
    __slots__ = ('status_icon', 'description', 'status',
                 'start_time', 'dash', 'end_time',
                 'button', 'button_icon', 'button_hover')

    def __init__(self, data: TransactionListItemData, rect: QRect):
        self._calculate_rectangles(data, rect, TransactionDistances())

    def _calculate_rectangles(self, data: TransactionListItemData, rect: QRect, distances: TransactionDistances):
        self.status_icon = QRect(
            distances.left_padding,
            distances.top_padding + distances.icon_top_padding,
            distances.icon_width,
            distances.icon_height
        )

        self.description = QRect(
            self.status_icon.right() + distances.horizontal_spacing,
            distances.top_padding,
            _text_pixel_width(data.description, TransactionFonts().top),
            top_height()
        )

        self.status = QRect(
            self.status_icon.right() + distances.horizontal_spacing,
            self.description.bottom() + 1,
            _text_pixel_width(get_state_text(data), TransactionFonts().bottom),
            bottom_height()
        )

        start_time_width = _text_pixel_width(get_start_time(data), TransactionFonts().top)
        dash_width = _text_pixel_width(get_dash(), TransactionFonts().top)
        end_time_width = _text_pixel_width(get_end_time(data), TransactionFonts().top)

        time_width = start_time_width + dash_width + end_time_width

        self.start_time = QRect(
            rect.right() - distances.right_padding - time_width,
            distances.top_padding,
            start_time_width,
            top_height()
        )
        self.dash = QRect(
            self.start_time.right(),
            distances.top_padding,
            dash_width,
            top_height()
        )
        self.end_time = QRect(
            self.dash.right(),
            distances.top_padding,
            end_time_width,
            top_height()
        )

        self._calculate_button_rectangles(distances, data)

        self._crop(distances)
        self._translate(rect)

    def _calculate_button_rectangles(self, distances: TransactionDistances, data: TransactionListItemData):
        button_kind = data.button_to_display
        button_text = get_button_text(button_kind)
        button_width = _text_pixel_width(button_text, TransactionFonts().button)
        button_height = _text_pixel_height(button_text, TransactionFonts().button)
        button_label_height = distances.button_height - distances.button_vertical_margin * 2
        self.button = QRect(
            self.start_time.left() - distances.horizontal_spacing - distances.button_horizontal_margin - button_width,
            distances.top_padding + distances.button_vertical_margin + (button_label_height - button_height) // 2,
            button_width,
            button_height
        )
        self.button_icon = QRect(
            self.button.left() - distances.button_horizontal_spacing - distances.button_icon_width,
            int(distances.top_padding + distances.button_vertical_margin +
                (button_label_height - distances.button_icon_height) / 2),
            distances.button_icon_width,
            distances.button_icon_height
        )
        self.button_hover = QRect(
            self.button_icon.left() - distances.button_horizontal_margin,
            distances.top_padding,
            (self.button.right() + distances.button_horizontal_margin -
             (self.button_icon.left() - distances.button_horizontal_margin)),
            distances.button_height
        )

    def _crop(self, distances: TransactionDistances):
        self.description.setRight(min(self.description.right(),
                                      self.button_hover.left() - distances.horizontal_spacing))
        self.status.setRight(min(self.status.right(),
                                 self.button_hover.left() - distances.horizontal_spacing))

    def _translate(self, rect: QRect):
        for rect_name in self.__slots__:
            try:
                getattr(self, rect_name).translate(rect.topLeft())
            except AttributeError:
                pass

    @classmethod
    @lru_cache
    def preferred_height(cls) -> int:
        return (bottom_height() + top_height() + TransactionDistances().top_padding +
                TransactionDistances().bottom_padding)
