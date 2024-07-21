import html
import re
import time
from functools import lru_cache, cached_property, reduce
from typing import Set, Union, Optional, Sequence, Tuple, Dict

from tons.ui.gui.utils import REGEXP_HTML_TAG, clean_html

HTML_ENTITIES = ['&lt;', '&gt;', '&amp;', '&nbsp;']


@lru_cache(maxsize=2048)  # when source string is the same, return the same instance
class RichString:
    def __init__(self, string: str):
        if not isinstance(string, str):
            raise TypeError("String expected as a constructor argument")

        self._string = string
        self._get_slice = lru_cache(1024)(self.__get_slice)
        self._entity_at = lru_cache(4096)(self.__entity_at)
        self.rich_index = lru_cache(4096)(self.__rich_index)
        self._should_increase_rich_index = lru_cache(4096)(self.__should_increase_rich_index)

    @property
    def string(self) -> str:
        return self._string

    @cached_property
    def clean_string(self) -> str:
        """
        String without tags, and with entities unescaped.

        Example:
            >> RichString('he<b>ll</b>o').clean_string
            hello

            >> RichString('he&lt;llo').clean_string
            he<llo

        """
        return html.unescape(clean_html(self.string))

    @cached_property
    def html_indexes(self) -> Set:
        """
        Example:
            >> RichString('he<b>ll</b>o').html_indexes
            {2, 3, 4, 7, 8, 9, 10}  #  he<b>ll</b>o
                                    #    ^^^  ^^^^
        """
        return {
            idx
            for match in REGEXP_HTML_TAG.finditer(self.string)
            for idx in range(match.start(), match.end())
        }

    @cached_property
    def entity_indexes(self) -> Set:
        """
        Example:
            >> RichString('he&lt;ll&gt;o').entity_indexes
            {2, 3, 4, 5, 8, 9, 10, 11}  #  he&lt;ll&gt;o
                                        #    ^^^^  ^^^^
        """
        sets = (
            {
                idx
                for match in re.finditer(_escaped_symbol, self.string)
                for idx in range(match.start(), match.end())
            }
            for _escaped_symbol in HTML_ENTITIES
        )

        return reduce(lambda x, y: x | y, sets, set())

    @cached_property
    def rich_length(self) -> int:
        """ Length of a string without html tags, and html entities unescaped

        Example:
            >> rs = RichString('he<b>ll</b>&lt;o')
            >> rs.rich_length
            6

        """
        return len(self.clean_string)

    def is_tag(self, index: int) -> bool:
        return index in self.html_indexes

    def is_entity(self, index: int) -> bool:
        return index in self.entity_indexes

    def __rich_index(self, index: int) -> int:
        """ Index in a string without html tags, and html entities unescaped

        Example:
            >> rs = RichString('he<b>ll</b>o')
            >> rs.rich_index(5)
            2  #  hello
               #    ^

        Example:
            >> rs = RichString('he&gt;llo')
            >> rs.rich_index(2)
            2  #  he>llo
               #    ^
            >> rs.rich_index(3)
            2  #  characters from 2 to 5 are inside the html entity
               #  he>llo
               #    ^

        Example:
            >> rs = RichString('he<b>ll</b>o')
            >> rs.rich_index(2)
            IndexError  #  2 is inside an html tag
                        #  he<b>ll</b>o
                        #    ^

        Example:
            >> rs = RichString('<b><i></i></b>')
            >> rs.rich_index(0)
            IndexError  # string is empty, it only consists of HTML tags

        """
        if not isinstance(index, int):
            raise TypeError("int expected")

        if index < 0:
            index += len(self.string)

        if index < 0 or index >= len(self.string):
            raise IndexError('Index out of range')

        if self.is_tag(index):
            raise IndexError('Symbol inside HTML tag')

        rich_idx = -1
        for i in range(len(self.string)):
            if self._should_increase_rich_index(i):
                rich_idx += 1

            if i == index:
                break

        if rich_idx < 0:
            raise IndexError('String only contains HTML tags')

        return rich_idx

    def plain_indexes(self, rich_index: Union[int, Sequence[int]]) -> Set[int]:
        """ Get indexes inside the string with html tags and escaped html entities

        Example:
            >> rs = RichString('he<b>ll</b>o')
            >> rs.plain_indexes(2)
            {5}  # he<b>ll</b>o
                 #      ^

        Example:
            >> rs = RichString('he&gt;llo')
            >> rs.plain_indexes(2)
            {2, 3, 4, 5}  # he&gt;llo
                          #   ^^^^

        Example:
            >> rs = RichString('he<b>ll</b>o')
            >> rs.plain_indexes([0,1,2])
            {0, 1, 5}  # he<b>ll</b>o
                       # ^^   ^

        """
        try:
            iter(rich_index)
        except TypeError:
            pass
        else:
            return reduce(lambda x, y: x | y, map(self.plain_indexes, rich_index), set())

        if not isinstance(rich_index, int):
            raise TypeError("int expected")

        if rich_index < 0:
            rich_index += self.rich_length

        if rich_index < 0 or rich_index >= self.rich_length:
            raise IndexError('Index out of range')

        cur_rich_idx = -1
        for i in range(len(self.string)):
            if self._should_increase_rich_index(i):
                cur_rich_idx += 1

            if cur_rich_idx == rich_index:
                break
        else:
            raise IndexError

        result = {i}

        if self.is_entity(i):
            result |= set(range(i, i + len(self._entity_at(i))))

        return result

    def __entity_at(self, i: int) -> str:
        """
        Raises:
            StopIteration if not found
        """
        return next(e for e in HTML_ENTITIES if self.string[i:].startswith(e))

    def __should_increase_rich_index(self, i: int) -> bool:
        if self.is_tag(i):
            return False

        if self.is_entity(i):
            try:
                self._entity_at(i)
            except StopIteration:
                return False  # not the first symbol of entity
            else:
                return True  # first symbol of entity

        return True

    def __getitem__(self, item: Union[int, slice]) -> str:
        """
        Example:
            >> rs = RichString('He<b>ll</b>o World! My <i>name</i> is Andrey')
            >> rs[:11]
            'He<b>ll</b>o World<i></i>'
            >> rs[5:]
            '<b></b> World! My <i>name</i> is Andrey'
            >> rs[2]
            '<b>l</b><i></i>'
            >> rs[::2]
            'H<b>l</b>oWrd y<i>nm</i> sAde'
            >> rs[-5:]
            '<b></b><i></i>ndrey'
            >> rs[::-1]
            ValueError('Slices with negative steps are not supported')
            >> RichString('he&lt;llo')[:3]
            'he&lt;'
        """
        if isinstance(item, slice):
            try:
                if item.step < 0:
                    raise ValueError('Slices with negative steps are not supported')
            except TypeError:
                pass
            item = item.start, item.stop, item.step

        elif not isinstance(item, int):
            raise TypeError(f'Slice or int expected, got {type(item)}')

        return self._get_slice(item)

    def __get_slice(self, item: Union[int, Tuple[Optional[int], Optional[int], Optional[int]]]) -> str:
        if isinstance(item, tuple):
            # this is required because slice object is not hashable
            item = slice(item[0], item[1], item[2])

        rich_indexes_to_include = range(self.rich_length)[item]
        indexes_to_include = self.html_indexes | self.plain_indexes(rich_indexes_to_include)
        symbols_to_include = (symbol for idx, symbol in enumerate(self.string) if idx in indexes_to_include)
        return ''.join(symbols_to_include)

    def __len__(self) -> int:
        return self.rich_length

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.string)})'

    def __str__(self) -> str:
        return self.string


def _test_1():
    string = 'he<b>ll</b>o'
    same_string = 'he<b>ll</b>o'
    other_string = 'He<b>ll</b>o World! My <i>name</i> is Andrey'

    rs1 = RichString(string)
    rs2 = RichString(same_string)
    rs3 = RichString(other_string)

    assert rs1 is rs2
    assert rs2 is not rs3
    print('test 1 complete')


def _test_2():
    assert RichString('he<b>ll</b>o').html_indexes == {2, 3, 4, 7, 8, 9, 10}
    print('test 2 complete')


def _test_3():
    rs = RichString('He<b>ll</b>o World! My <i>name</i> is Andrey')
    assert rs[:11] == 'He<b>ll</b>o World<i></i>'
    assert rs[5:] == '<b></b> World! My <i>name</i> is Andrey'
    assert rs[2] == '<b>l</b><i></i>'
    assert rs[::2] == 'H<b>l</b>oWrd y<i>nm</i> sAde'
    assert rs[-5:] == '<b></b><i></i>ndrey'
    assert rs[-1] == '<b></b><i></i>y'
    try:
        rs[::-1]
    except ValueError:
        pass
    else:
        assert False
    print('test 3 complete')


def _test_4():
    rs = RichString('x &lt; y * z')
    assert rs[:0] == ''
    assert rs[:2] == 'x '
    assert rs[:3] == 'x &lt;'
    assert rs[2:] == '&lt; y * z'
    assert rs[2] == '&lt;'
    assert rs[::2] == 'x&lt;y*z'
    print('test 4 complete')


def _test_5():
    assert RichString('')[:0] == ''

    rs = RichString('New wallet 001 &lt;&gt;?$&amp;@!&lt;')
    assert rs[:15] == 'New wallet 001 '
    assert rs[15] == '&lt;'
    assert rs[16] == '&gt;'
    assert rs[15:] == '&lt;&gt;?$&amp;@!&lt;'
    assert rs[-1] == '&lt;'
    print('test 5 complete')


def _unit_test():
    _test_1()
    _test_2()
    _test_3()
    _test_4()
    _test_5()


def _speed_test():
    start = time.time()
    n = 100000
    for _ in range(n):
        rs = RichString('He<b>ll</b>o World! My <i>name</i> is Andrey')
        assert rs[:11] == 'He<b>ll</b>o World<i></i>'
        assert rs[5:] == '<b></b> World! My <i>name</i> is Andrey'
        assert rs[2] == '<b>l</b><i></i>'
        assert rs[::2] == 'H<b>l</b>oWrd y<i>nm</i> sAde'
        assert rs[-5:] == '<b></b><i></i>ndrey'

    print('speed test evaluated in', time.time() - start, f'{n=}')


if __name__ == "__main__":
    _unit_test()
    _speed_test()

__all__ = ['RichString']
