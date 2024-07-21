from enum import Enum, auto
from functools import lru_cache
from typing import Tuple, Optional, Dict, Union

from PyQt6.QtGui import QFont

from tons.ui.gui.utils import clean_html, text_pixel_width
from tons.ui.gui.utils._rich_string import RichString


class RichTextElideMode(Enum):
    left = auto()  # bite from left
    right = auto()  # bite from right
    center = auto()  # bite from center


@lru_cache(maxsize=4096)
def elide_rich_text(rich_text: str, max_width: Union[int, float],
                    font: Optional[QFont] = None,
                    elide_mode: RichTextElideMode = RichTextElideMode.center) -> str:
    return _RichTextElider(rich_text, max_width, font, elide_mode).elided_text


class _RichTextElider:
    def __init__(self, rich_text: str, max_width: Union[int, float], font: Optional[QFont], elide_mode: RichTextElideMode = RichTextElideMode.center):
        self._text = rich_text
        self._elided_text = rich_text
        self._rich_string = RichString(rich_text)
        if self._rich_string.clean_string == rich_text:
            self._rich_string = rich_text
        self._font = font
        self._elide_mode = elide_mode
        self._max_width = max_width
        self._left_slice, self._right_slice = self._init_slices()
        self._text_width_cache: Dict[str, float] = dict()

        self._elide()

    @property
    def elided_text(self) -> str:
        return self._elided_text

    def _init_slices(self) -> Tuple[Optional[slice], Optional[slice]]:
        if self._elide_mode == RichTextElideMode.center:
            center = len(self._rich_string) // 2
            return slice(None, center), slice(center, None)

        elif self._elide_mode == RichTextElideMode.left:
            return None, slice(0, None)

        elif self._elide_mode == RichTextElideMode.right:
            len_ = len(self._rich_string)
            return slice(None, len_), None

        else:
            raise NotImplementedError

    def _text_pixel_width(self) -> float:
        try:
            return self._text_width_cache[self._elided_text]
        except KeyError:
            pass

        width = text_pixel_width(self._elided_text, self._font)
        self._text_width_cache[self._elided_text] = width

        return width

    def _elide(self):
        try:
            self.__elide()
        except ZeroDivisionError as exc:
            """ either _max_width or _text_pixel_width() is zero"""
            self._elided_text = ''

    def __elide(self):
        if self._text_pixel_width() < self._max_width or clean_html(self._elided_text) == '...':
            """ No need to elide """
            return

        """ Guess the required length by dividing text pixel width by max width"""
        self._make_educated_guess()

        if self._text_pixel_width() > self._max_width:
            self._shorten_until_fits()
        elif self._text_pixel_width() < self._max_width:
            self._lengthen_until_still_fits()

    def _make_educated_guess(self):
        target_len = int(len(self._rich_string) * self._max_width // self._text_pixel_width())
        target_len = max(target_len, len('...'))

        """ Shorten to guessed length"""
        # Quick shorten
        cur_len = len(self._rich_string)
        delta = cur_len - target_len + len('...')
        if self._elide_mode == RichTextElideMode.center:
            delta //= 2
        self._shorten_slices(delta)

        # Linear shorten
        safety_exit = 10000
        while safety_exit > 0:
            if self._get_elided_text_length_from_slices() <= target_len:
                break
            self._shorten_slices(1)
            safety_exit -= 1
        else:
            assert False, 'Broken logic, safety exit reached'

        self._elided_text = self._get_elided_text()

    def _shorten_until_fits(self):
        safety_exit = 10000
        while safety_exit > 0:
            if self._text_pixel_width() < self._max_width or clean_html(self._elided_text) == '...':
                return

            self._shorten_further()
            safety_exit -= 1
        else:
            assert False, 'Broken logic, safety exit reached'

    def _get_slice(self, slice_object: Optional[slice]) -> str:
        if slice_object is None:
            return ''
        return self._rich_string[slice_object]

    def _get_elided_text(self):
        strings = list(map(self._get_slice, [self._left_slice, self._right_slice]))
        strings.insert(1, '...')
        return ''.join(strings)

    def _get_elided_text_length_from_slices(self) -> int:
        def get_slice_length(slc: Optional[slice]) -> int:
            if slc is None:
                return 0
            return len(range(0, len(self._rich_string))[slc])

        left = get_slice_length(self._left_slice)
        right = get_slice_length(self._right_slice)
        return left + len('...') + right

    def _shorten_further(self):
        self._shorten_slices(1)
        self._elided_text = self._get_elided_text()

    def _shorten_slices(self, delta: int):
        if self._elide_mode in [RichTextElideMode.right, RichTextElideMode.center]:
            self._left_slice = slice(self._left_slice.start, self._left_slice.stop - delta)
        if self._elide_mode in [RichTextElideMode.left, RichTextElideMode.center]:
            self._right_slice = slice(self._right_slice.start + delta, self._right_slice.stop)

    def _lengthen(self):
        self._lengthen_slices(1)
        self._elided_text = self._get_elided_text()

    def _lengthen_slices(self, delta: int):
        if self._elide_mode in [RichTextElideMode.right, RichTextElideMode.center]:
            self._left_slice = slice(self._left_slice.start, self._left_slice.stop + delta)
        if self._elide_mode in [RichTextElideMode.left, RichTextElideMode.center]:
            self._right_slice = slice(self._right_slice.start - delta, self._right_slice.stop)

    def _can_lengthen_further(self) -> bool:
        if self._elide_mode == RichTextElideMode.left:
            if self._right_slice.start == 0:
                return False
            assert self._right_slice.start > 0, 'Broken logic'

        if self._elide_mode == RichTextElideMode.center:
            if self._left_slice.stop == self._right_slice.start:
                return False
            assert (self._right_slice.start - self._left_slice.stop) >= 2, 'Broken logic'

        if self._elide_mode == RichTextElideMode.right:
            if self._left_slice.stop == len(self._rich_string):
                return False
            assert self._left_slice.stop < len(self._rich_string), 'Broken logic'

        return True

    def _lengthen_until_still_fits(self):
        assert self._text_pixel_width() <= self._max_width

        safety_exit = 10000

        while safety_exit > 0:
            if not self._can_lengthen_further():
                return

            previous_state = self._left_slice, self._right_slice, self._elided_text
            self._lengthen()
            if self._text_pixel_width() > self._max_width:
                self._left_slice, self._right_slice, self._elided_text = previous_state
                return

            safety_exit -= 1
        else:
            assert False, 'Broken logic, safety exit reached'


def _test_1():
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    string = 'Hello! My <i>name</i> is <b>Sergey</b>'

    for mode in RichTextElideMode:
        print('Mode:', mode)
        for max_width in [100, 50, 25]:
            elided_text = elide_rich_text(string, max_width, elide_mode=mode)
            print(f'   {max_width=}px   {elided_text}')
        print()


def _test_2():
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PyQt6.QtGui import QResizeEvent
    from PyQt6.QtWidgets import QLayout
    from PyQt6.QtWidgets import QSizePolicy

    class MyLabel(QLabel):
        def __init__(self, elide_mode: RichTextElideMode = RichTextElideMode.center):
            super().__init__()
            self._initial_text: Optional[str] = None
            self.setStyleSheet('border: 1px solid red')
            self._elide_mode = elide_mode

        def setText(self, txt: str):
            super().setText(txt)
            self._initial_text = txt

        def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
            super().setText(elide_rich_text(self._initial_text, self.width(), self.font(), self._elide_mode))


    app = QApplication([])

    widget = QWidget()
    layout = QVBoxLayout()
    layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
    widget.setLayout(layout)

    font = QFont()
    font.setPointSize(36)

    for elide_mode in RichTextElideMode:
        label = MyLabel(elide_mode)
        label.setFont(font)
        label.setText('Hello! My <i>name</i> is <b>Sergey</b>')
        label.setMinimumWidth(0)
        sp = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        label.setSizePolicy(sp)

        layout.addWidget(label)

    widget.show()

    app.exec()


def _tests():
    _test_1()
    _test_2()


if __name__ == '__main__':
    _tests()

__all__ = ['elide_rich_text', 'RichTextElideMode']
