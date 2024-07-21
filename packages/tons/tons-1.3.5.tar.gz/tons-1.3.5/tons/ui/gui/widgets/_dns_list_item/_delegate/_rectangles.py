from functools import lru_cache
from itertools import chain
from typing import Optional, Tuple, Sequence

from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QFont

from tons.ui.gui.utils import text_pixel_width
from ._model_getters import get_dns_name, get_expiring_verbal_and_digits
from ._text_constants import dns_visual_noise, filter_by_this_wallet, state_text, dot_ton
from .._item_data import DnsListItemData
from ._fonts import Fonts, bottom_height, top_height
from ._sizes import DnsItemDistances


@lru_cache(maxsize=1024)
def _text_pixel_width(text: str, font: QFont) -> int:
    return int(text_pixel_width(text, font) + 1)

@lru_cache
def _dns_visual_noise_width() -> int:
    return _text_pixel_width(dns_visual_noise(), Fonts().state)

@lru_cache
def _state_gap_width() -> int:
    return _text_pixel_width('__', Fonts().state)

@lru_cache
def _filter_by_this_wallet_width() -> int:
    return _text_pixel_width(filter_by_this_wallet(), Fonts().filter_by_this_wallet)

@lru_cache
def _max_expiring_width() -> int:
    max_verbal_width = max(_text_pixel_width('days', Fonts().expires_verbal),
               _text_pixel_width('hours', Fonts().expires_verbal))
    all_possible_digits = chain(
                map(str, range(367)),
                (
                    '{:02d}:{:02d}'.format(hours, minutes)
                    for hours, minutes in zip(range(0, 24), range(0, 60))
                )
            )
    max_digits_width = max(
        map(
            lambda text: _text_pixel_width(text, Fonts().expires_digits),
            all_possible_digits
        )
    )
    return max_verbal_width + max_digits_width


@lru_cache
def _minimum_wallet_address_width() -> int:
    return _text_pixel_width('(ABCD...EFGH)', Fonts().address)


class DnsItemRectangles:
    __slots__ = ('domain', 'dot_ton',
                 'filter_by_this_wallet', 'wallet_name', 'wallet_address', 'expiring_verbal',
                 'expiring_digits', 'visual_noise', 'state', 'icon', 'button',
                 'button_hover',)

    def __init__(self, data: DnsListItemData, rect: QRect, distances: Optional[DnsItemDistances] = None):
        self._calculate_rectangles(data, rect, distances or DnsItemDistances())

    def _calculate_rectangles(self, data: DnsListItemData, rect: QRect, distances: DnsItemDistances):
        self._calculate_rectangles_zero_padding(data,
                                                QRect(rect.x(),
                                                      rect.y(),
                                                      rect.width() - distances.left_padding - distances.right_padding,
                                                      rect.height() - distances.top_padding - distances.bottom_padding
                                                      ),
                                                distances
                                                )
        for rect_name in self.__slots__:
            try:
                getattr(self, rect_name).translate(rect.topLeft() + QPoint(distances.left_padding, distances.top_padding))
            except AttributeError:
                pass

    def _calculate_rectangles_zero_padding(self, data: DnsListItemData, rect: QRect, distances: DnsItemDistances):
        self.icon = QRect(0, distances.icon_top_margin, distances.icon_width, distances.icon_height)
        self.button = QRect(rect.width() - distances.button_width, 0,
                            distances.button_width, distances.button_height)
        self.button_hover = QRect(
            self.button.x() - distances.button_hover_margin,
            self.button.y() - distances.button_hover_margin,
            self.button.width() + 2 * distances.button_hover_margin,
            self.button.height() + 2 * distances.button_hover_margin
        )
        self._calculate_info_rectangles_zero_padding(data,
                                                     QRect(
                                                          rect.x(),
                                                          rect.y(),
                                                          rect.width()
                                                          - distances.icon_width
                                                          - distances.button_width
                                                          - distances.horizontal_spacing * 3,
                                                          rect.height()),
                                                     distances
                                                     )

        for rect in self.info_rectangles:
            rect.translate(distances.icon_width + distances.horizontal_spacing, 0)

    @property
    def info_rectangles(self) -> Sequence[QRect]:
        return [self.domain, self.dot_ton, self.wallet_name, self.wallet_address, self.expiring_verbal, self.expiring_digits,
                self.visual_noise, self.state, self.filter_by_this_wallet]

    def _calculate_info_rectangles_zero_padding(self, data: DnsListItemData, rect: QRect, distances: DnsItemDistances):
        self.domain = QRect(
            0,
            0,
            _text_pixel_width(get_dns_name(data), Fonts().domain),
            top_height()
        )
        self.dot_ton = QRect(
            self.domain.right(),
            0,
            _text_pixel_width(dot_ton(), Fonts().domain),
            top_height()
        )

        # Expiring in
        verbal, digits = self._expiring_verbal_and_digits(data)
        top_right_width = (_text_pixel_width(verbal, Fonts().expires_verbal) +
                           _text_pixel_width(digits + '&nbsp;', Fonts().expires_digits))
        top_right = QRect(
            rect.width() - top_right_width,
            0,
            top_right_width,
            top_height()
        )
        verbal_width = _text_pixel_width(verbal, Fonts().expires_verbal)
        digit_width = _text_pixel_width(digits, Fonts().expires_digits)
        self.expiring_verbal = QRect(top_right)
        self.expiring_verbal.setWidth(verbal_width)
        self.expiring_digits = QRect(top_right)
        self.expiring_digits.setLeft(self.expiring_digits.right() - digit_width)

        central_column_width = self._central_column_width(rect)
        top_center = QRect(
            rect.width() - central_column_width - _max_expiring_width() - 2 * distances.horizontal_spacing,
            0,
            central_column_width,
            top_height()
        )

        # Circumcise
        top_center.setRight(self.expiring_verbal.left() - distances.horizontal_spacing)
        if top_center.left() - distances.horizontal_spacing < self.dot_ton.right():
            self.dot_ton.setWidth(0)

        self.domain.setRight(min(self.domain.right(), top_center.left() - distances.horizontal_spacing))

        self._calculate_wallet_rectangles(top_center, data.wallet_name, data.wallet_address, distances)

        y_bottom = rect.height() - bottom_height()

        # Bottom rectangles
        self.filter_by_this_wallet = QRect(self.wallet_name.left(),
                                           y_bottom,
                                           _filter_by_this_wallet_width(),
                                           bottom_height())

        self.visual_noise = QRect(0, y_bottom, _dns_visual_noise_width(), bottom_height())
        self.state = QRect(0, y_bottom,
                           self.filter_by_this_wallet.left() - distances.horizontal_spacing, bottom_height())
        self.state.setLeft(_dns_visual_noise_width() + _state_gap_width())

        for r in [self.state, self.visual_noise]:
            r.setRight(min(r.right(), self.filter_by_this_wallet.left() - distances.horizontal_spacing))

        if self.state.width() < _text_pixel_width(state_text(data.kind), Fonts().state) + 1:
            # Hide visual noise if state does not fit
            self.state.setLeft(self.state.right() - _text_pixel_width(state_text(data.kind), Fonts().state))
            self.visual_noise.setRight(self.state.left() - _state_gap_width())

    def _calculate_wallet_rectangles(self, top_center: QRect, wallet_name: str, wallet_address: str,
                                     distances: DnsItemDistances):
        wallet_name_width = _text_pixel_width(wallet_name + '  ', Fonts().wallet_name)
        self.wallet_name = QRect(top_center)
        self.wallet_name.setWidth(wallet_name_width)
        self.wallet_name.setRight(min(self.wallet_name.right(), top_center.right()))

        self.wallet_address = QRect(top_center)
        self.wallet_address.setLeft(top_center.left() + wallet_name_width)

        if self.wallet_address.width() < _minimum_wallet_address_width():
            self.wallet_address.setLeft( top_center.right() - _minimum_wallet_address_width() )
            self.wallet_name.setRight( self.wallet_address.left() )

        self.wallet_address.setRight(min(self.wallet_address.right(), top_center.right()))
        self.wallet_name.setRight(min(self.wallet_name.right(), top_center.right()))

    def _central_column_width(self, rect: QRect) -> int:
        return rect.width() // 2

    def _top_left_width(self, data: DnsListItemData) -> int:
        return _text_pixel_width(get_dns_name(data), Fonts().domain)

    def _expiring_verbal_and_digits(self, data: DnsListItemData) -> Tuple[str, str]:
        return get_expiring_verbal_and_digits(data)

    @classmethod
    @lru_cache
    def preferred_height(cls) -> int:
        return bottom_height() + top_height() + DnsItemDistances.top_padding + DnsItemDistances.bottom_padding

