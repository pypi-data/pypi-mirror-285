import base64
import contextlib
import math
import os
import random
import re
import sys
import tempfile
import webbrowser
from abc import ABCMeta
from decimal import Decimal
from functools import wraps, lru_cache
from pathlib import Path
from typing import Optional, Union, Tuple, List, Any, Callable, Sequence, Iterator

from PIL.Image import Image
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import QObject, QLocale, QSizeF, Qt, QUrl, QSize
from PyQt6.QtGui import QScreen, QPixmap, QFontDatabase, QStandardItemModel, QIcon, QDoubleValidator, QValidator, \
    QFontMetrics, QFont, QColor, QPalette, QTextDocument, QTextBlock, QDesktopServices
from PyQt6.QtWidgets import QApplication, QWidget, QPlainTextEdit, QComboBox, QLineEdit, QToolButton, QLabel, \
    QGraphicsBlurEffect

from tons.logging_ import tons_logger
from tons.tonclient._client._base import AddressState
from tons.tonsdk.utils import Address
from tons.ui.gui._settings import TONS_GUI_FONTS_DIR, TONS_GUI_LIGHT_ICONS_DIR, TONS_GUI_DARK_ICONS_DIR


def scanner_base_url(testnet: bool) -> str:
    if testnet:
        return "https://testnet.tonscan.org/"
    return "https://tonscan.org/"

def decorates(original_class: type):
    """
    Analogue of functools.wraps for classes.
    https://stackoverflow.com/questions/69372666/decorating-a-class-with-the-correct-names
    """
    def magic(decorated_class: type):
        for attr in '__doc__', '__name__', '__qualname__', '__module__':
            setattr(decorated_class, attr, getattr(original_class, attr))
        return decorated_class
    return magic


def get_clear_button(line_edit: QLineEdit) -> QToolButton:
    assert line_edit.isClearButtonEnabled()
    clear_buttons = line_edit.findChildren(QToolButton)
    assert len(clear_buttons) == 1
    return clear_buttons[0]


def pil_to_pixmap(image: Image) -> QPixmap:
    """
    https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue
    All the answers either lead to a distorted image or crash the app.
    So it has been decided to save the PIL image to a temp file and read it to QPixmap, as the safest option.
    """
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_image_file:
        tmp_image_path = tmp_image_file.name

    image.save(tmp_image_path)
    pixmap = QPixmap(tmp_image_path)

    os.remove(tmp_image_path)
    return pixmap


def move_to_center(widget: QWidget, parent_widget: Union[QWidget, QScreen]):
    try:
        parent_geometry = parent_widget.geometry()
    except AttributeError:
        parent_geometry = parent_widget.availableGeometry()

    parent_center = parent_geometry.center()
    geometry = widget.geometry()
    geometry.moveCenter(parent_center)
    widget.setGeometry(geometry)


class QABCMeta(type(QObject), type(ABCMeta)):
    """ Should be usea as a metaclass if you want to make a QObject child abstract"""
    pass


def wallet_state_with_circle(state: Optional[AddressState], circle_first: bool = True) -> str:
    if state is None:
        return ''
    matrix = {
        AddressState.uninit: '⚪',
        AddressState.active: '🟢',
        AddressState.frozen: '🔵',
        AddressState.non_exist: '◯'
    }
    if circle_first:
        return matrix[state] + ' ' + str(state.value)
    else:
        return str(state.value) + ' ' + matrix[state]


def xstr(val) -> str:
    if val is None:
        return ''
    return str(val)


def dashstr(val) -> str:
    if val is None:
        return '-'
    return str(val)


def nastr(val) -> str:
    if val is None:
        return '(n/a)'
    return str(val)


@lru_cache(maxsize=1024)
def pretty_balance(balance: Optional[Decimal], decimals: int = 9, gray_decimal_part: bool = True) -> str:
    """
    Example:
         >> pretty_balance(Decimal('5544332211.12345678'))
         '5 544 332 211.<span style="color: gray">123 456 780</span>'
         >> pretty_balance(Decimal('5544332211.12345678', 8))
         '5 544 332 211.<span style="color: gray">123 456 78</span>'
         >> pretty_balance(Decimal('5544332211.12345678', 8))
    """
    if balance is None:
        return ''

    def separate_thousands(value: int, sep=' ') -> str:
        return format(value, ',').replace(',', sep)

    format_ = f'.{decimals}f'
    balance = format(balance, format_)
    split = balance.split('.')

    integer_part = separate_thousands(int(split[0]))

    try:
        decimal_part = split[1]
    except IndexError:
        return integer_part

    to_join = []
    for i in range((decimals + 1) // 3):
        to_join.append(decimal_part[3*i:3*i+3])
    decimal_part = '.' + ' '.join(to_join)

    if gray_decimal_part:
        decimal_part = html_text_colored(decimal_part, 'gray')

    return f'{integer_part}{decimal_part}'


def ton_balance_validator() -> QValidator:
    validator = QDoubleValidator()
    validator.setBottom(0.0)
    validator.setDecimals(9)
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    locale = QLocale("C")
    locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    validator.setLocale(locale)
    return validator


def pretty_fiat_balance(balance_fiat: Optional[Decimal], fiat_symbol: str) -> str:
    if balance_fiat is None:
        return ''
    return f'{fiat_symbol}{pretty_balance(balance_fiat, decimals=2, gray_decimal_part=False)}'


def __set_default_macos_font():
    font = QFont()
    font.setFamily('SF Pro Display')
    font.setStyleHint(QFont.StyleHint.System)
    QApplication.setFont(font)


def setup_fonts():
    font_filenames = os.listdir(TONS_GUI_FONTS_DIR)

    for font_filename in font_filenames:
        font_path = os.path.join(TONS_GUI_FONTS_DIR, font_filename)
        if QFontDatabase.addApplicationFont(os.path.abspath(font_path)) < 0:
            tons_logger().warn(f"warning: failed to load font {font_path}")

    if macos():
        __set_default_macos_font()


def copy_to_clipboard(text: str):
    cb = QApplication.clipboard()
    cb.setText(text)
    tons_logger().debug(f'copied: {text[:3] + "..."}')


def available_wallet_versions() -> Tuple[str, ...]:
    return 'v2r1', 'v2r2', 'v3r1', 'v3r2', 'v4r1', 'v4r2'


def available_workchains() -> Tuple[int, ...]:
    return 0, -1


def available_workchains_hints() -> Tuple[str, ...]:
    return '(Basechain)', '(Masterchain)'


@lru_cache(maxsize=256)
def workchain_with_hint_text(workchain_val: int, palette: Optional[QPalette] = None) -> str:
    col = blended_hint_color(palette)
    text_hint = ""
    if workchain_val == 0:
        text_hint = ' ' + html_text_colored('(Basechain)', col)
    elif workchain_val == -1:
        text_hint = ' ' + html_text_colored('(Masterchain)', col)

    return f"{workchain_val}{text_hint}"


def disable_scrolling(plain_text_edit: QPlainTextEdit):
    def dummy(_x, _y):
        pass

    plain_text_edit.scrollContentsBy = dummy


def clone_qmodel(src: QStandardItemModel, dst: QStandardItemModel):
    dst.clear()
    for i in range(src.rowCount()):
        row = src.item(i)
        dst.appendRow(row.clone())


_combo_max_width_memo = dict()  # for storing true max width set in the designer that is overwritten by setFixedWidth()


def adjust_size_independently(combo_box: QComboBox):
    """ Adjust
    - closed widget to fit current item size
    - drop-down list to fit longest item """
    if type(combo_box).__name__ == 'LocationSelectComboBox':
        return

    icons: List[QIcon] = [combo_box.itemIcon(i) for i in range(combo_box.count())]
    items: List[str] = [combo_box.itemText(i) for i in range(combo_box.count())]
    data: List[Any] = [combo_box.itemData(i) for i in range(combo_box.count())]

    current_index = combo_box.currentIndex()
    current_icon = icons[current_index]
    current_text = items[current_index]

    _combo_max_width_memo[combo_box] = _combo_max_width_memo.get(combo_box, combo_box.maximumWidth())
    max_width = _combo_max_width_memo[combo_box]

    """ Current item size """
    combo_box.clear()
    combo_box.addItem(current_icon, current_text)
    size_hint = combo_box.sizeHint()
    width = size_hint.width()
    if macos():
        width += 10  # FIXME

    combo_box.setFixedWidth(min(width, max_width))

    """ Drop down list size """
    combo_box.clear()
    for idx, (icon, item, datum) in enumerate(zip(icons, items, data)):
        combo_box.addItem(icon, item)
        combo_box.setItemData(idx, datum)
    size_hint = combo_box.minimumSizeHint()
    width = size_hint.width()
    combo_box.view().setFixedWidth(min(width, max_width))

    combo_box.setCurrentIndex(current_index)


@contextlib.contextmanager
def suppress_combo_index_change(combo: QComboBox, reconnect_slots: Sequence[Callable]):
    index_changed_signal = combo.currentIndexChanged
    index_changed_signal.disconnect()
    yield
    for slot in reconnect_slots:
        index_changed_signal.connect(slot)


def macos() -> bool:
    return sys.platform.startswith('darwin')


def windows() -> bool:
    return sys.platform.startswith('win')


def set_expand_tooltip(widget: QWidget, value: str, max_length: int):
    if len(value) > max_length:
        widget.setToolTip(value)
    else:
        widget.setToolTip(None)


def get_elided_text(text: str, font: QFont, max_allowed_width: int) -> str:
    return QFontMetrics(font).elidedText(text, Qt.TextElideMode.ElideRight, max_allowed_width)


_numbers_for_gibberish = [math.pi, math.e] + [math.sqrt(x) for x in set(range(2,100)) - {4, 9, 16, 25, 36, 49, 64, 81}]


def gibberish(fake_length: int = 9) -> str:
    number = random.choice(_numbers_for_gibberish)
    return str(int(number * (10 ** (fake_length-1))))


def set_widget_obscure(widget: QWidget, obscure: bool):
    effect = QGraphicsBlurEffect()
    effect.setBlurRadius(10)
    if not obscure:
        effect = None
    widget.setGraphicsEffect(effect)


REGEXP_HTML_TAG = re.compile('<.*?>')


@lru_cache(maxsize=512)
def clean_html(raw_html: str) -> str:
    return re.sub(REGEXP_HTML_TAG, '', raw_html)


def _distance(rgb1, rgb2):
    """Euclidean distance"""
    s = 0
    for i in range(3):
        s += (rgb1[i] - rgb2[i]) ** 2
    s = s ** .5
    return s


@lru_cache
def theme_is_dark() -> bool:  # TODO DRY (added here due to circular imports)
    theme_text_color = QApplication.palette().text().color()
    theme_text_color = theme_text_color.red(), theme_text_color.green(), theme_text_color.blue()
    black = (0, 0, 0)
    white = (255, 255, 255)
    return _distance(theme_text_color, white) < _distance(theme_text_color, black)


def setup_palette(app: QApplication):
    palette = app.palette()
    cr = palette.ColorRole
    cg = palette.ColorGroup
    if macos() and theme_is_dark():
        text_color = QColor(0xeb, 0xeb, 0xf5, 0xd9)

        for color_group in [cg.Active, cg.Inactive]:
            for color_role in [cr.WindowText, cr.Text, cr.ButtonText]:
                palette.setColor(color_group, color_role, text_color)

    app.setPalette(palette)


@lru_cache(maxsize=None)
def validation_error_color() -> QColor:
    alpha = 0xBF if theme_is_dark() else 0xFF
    return QColor(0xED, 0x6A, 0x5F, alpha)


@lru_cache(maxsize=None)
def very_valid_color() -> QColor:
    return QColor(46, 204, 113, 0xBF)


@lru_cache(maxsize=None)
def line_edit_border_color() -> QColor:
    return QColor(0xFF, 0xFF, 0xFF, 0x26)


def font_family_available(family: str) -> bool:
    return any(family in f for f in QFontDatabase.families())


@lru_cache
def mono_font_face() -> str:
    if macos():
        macos_mono_family = 'SF Mono'
        if font_family_available(macos_mono_family):
            return macos_mono_family

    return 'Liberation Mono'


@lru_cache(maxsize=None)
def mono_font() -> QFont:
    font = QFont()
    font.setFamily(mono_font_face())
    font.setPointSize(font.pointSize() + 1)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 103)
    font.setStyleHint(QFont.StyleHint.TypeWriter)
    return font


@lru_cache(maxsize=None)
def extra_small_font() -> QFont:
    font = QFont()
    font.setPointSize(font.pointSize() - 3)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 100)
    return font


def blend_alpha(background_color: QColor, text_color: QColor, text_alpha: float) -> QColor:
    back_red, back_green, back_blue = background_color.red(), background_color.green(), background_color.blue()
    text_red, text_green, text_blue = text_color.red(), text_color.green(), text_color.blue()

    return QColor(
        int((1-text_alpha)*back_red + text_red * text_alpha),
        int((1-text_alpha)*back_green + text_green * text_alpha),
        int((1-text_alpha)*back_blue + text_blue * text_alpha)
    )


def invert_color(color: QColor) -> QColor:
    r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
    return QColor(0xff - r, 0xff - g, 0xff - b, a)


def set_selection_color_for_light_theme(widget: QWidget):
    if theme_is_dark():
        return
    palette = widget.palette()
    col = palette.color(QPalette.ColorRole.Highlight)
    col.setAlpha(int(0.50 * 0xff))
    palette.setColor(QPalette.ColorRole.Highlight, col)
    widget.setPalette(palette)


@lru_cache(maxsize=128)
def rich_text_document(text: str, font: Optional[QFont] = None) -> QTextDocument:
    td = QTextDocument()
    td.setHtml(text)
    if font is not None:
        td.setDefaultFont(font)
    td.setDocumentMargin(0)
    return td


@lru_cache(maxsize=512)
def text_pixel_size(text: str, font: Optional[QFont]) -> QSizeF:
    td = rich_text_document(text, font)
    return td.size()


def text_pixel_width(text: str, font: Optional[QFont]) -> float:
    return text_pixel_size(text, font).width()


def text_pixel_height(text: str, font: Optional[QFont]) -> float:
    return text_pixel_size(text, font).height()


def blended_text_color(alpha: float, palette: Optional[QPalette] = None,
                       background_role: QPalette.ColorRole = QPalette.ColorRole.Window) -> QColor:
    palette = palette or QPalette()
    background_color = palette.color(background_role)
    text_color = palette.color(QPalette.ColorRole.WindowText)

    blended_color = blend_alpha(background_color, text_color, alpha)
    return blended_color


def blended_hint_color(palette: Optional[QPalette] = None) -> QColor:
    return blended_text_color(0.15, palette)


def text_document_blocks(doc: QTextDocument) -> Iterator[QTextBlock]:
    block = doc.begin()
    while block != doc.end():
        yield block
        block = block.next()


def html_text_styled(text: str, style: str) -> str:
    return f'<span style="{style}">{text}</span>'


def html_text_colored(text: str, color: Union[QColor, str]) -> str:
    if isinstance(color, QColor):
        color = color.name(QColor.NameFormat.HexArgb)

    return html_text_styled(text, f"color: {color};")


def html_text_font(text: str, family=None, size=None, weight=None) -> str:
    style = ''

    if family is not None:
        style += f"font-family: {family}; "
    if size is not None:
        style += f"font-size: {size}; "
    if weight is not None:
        style += f"font-weight: {weight}; "

    return html_text_styled(text, style)


def set_blank_window_icon(widget: QWidget):
    icon = get_icon('blank.png')
    widget.setWindowIcon(icon)


@lru_cache(maxsize=None)
def get_icon(icon_name: str) -> QtGui.QIcon:
    icon = QtGui.QIcon()
    pixmap = get_icon_pixmap(icon_name)
    icon.addPixmap(pixmap, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    icon.addPixmap(pixmap, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
    return icon


@lru_cache(maxsize=None)
def get_icon_pixmap_size(icon_name: str) -> QSize:
    pixmap = get_icon_pixmap(icon_name)
    return pixmap.size()

@lru_cache(maxsize=None)
def get_icon_pixmap(icon_name: str) -> QtGui.QPixmap:
    icon_filepath = str(get_icons_directory() / icon_name)
    return QtGui.QPixmap(icon_filepath)


@lru_cache
def get_icons_directory() -> Path:
    if theme_is_dark():
        return TONS_GUI_LIGHT_ICONS_DIR
    return TONS_GUI_DARK_ICONS_DIR


@lru_cache(maxsize=None)
def get_icon_pixmap_rotated_180(icon_name: str) -> QtGui.QPixmap:
    return get_icon_pixmap_rotated(icon_name, 180)


@lru_cache(maxsize=128)
def get_icon_pixmap_rotated(icon_name: str, degrees: int) -> QtGui.QPixmap:
    """
    References:
        https://stackoverflow.com/questions/49475860/how-to-rotate-qpixmap-around-center-without-cutting-off-parts-of-the-image
    """
    original_pixmap = get_icon_pixmap(icon_name)

    width = original_pixmap.width()
    height = original_pixmap.height()

    rotated_pixmap = _empty_pixmap_with_alpha(width, height)

    painter = QtGui.QPainter(rotated_pixmap)

    painter.save()

    painter.translate(width//2, height//2)
    painter.rotate(degrees)
    painter.translate(-width//2, -height//2)

    render_rectangle = QtCore.QRect(0, 0, width, height)

    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(render_rectangle, original_pixmap)

    painter.restore()

    return rotated_pixmap


def _empty_pixmap_with_alpha(width: int, height: int) -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(width, height)
    color = QtGui.QColor(0)
    color.setAlpha(0)
    pixmap.fill(color)
    return pixmap


def set_icon(widget: Union[QtWidgets.QLabel, QtWidgets.QAbstractButton], icon_name: str):
    if isinstance(widget, QtWidgets.QLabel):
        widget.setPixmap(get_icon_pixmap(icon_name))
        widget.repaint()
    elif isinstance(widget, QtWidgets.QAbstractButton):
        icon = get_icon(icon_name)
        widget.setIcon(icon)
    else:
        raise NotImplementedError(f"Unknown widget type: {type(widget)}")


def fix_button_height_based_on_system(push_button: QtWidgets.QPushButton):
    """
    Fixes the `pushButton` height.

    `pushButton`s have a beautiful rounded style in MacOS when their height is set to exactly 32 pixels.
    This is not the case for Windows where buttons look best with height = 24.
    """
    if macos():
        geometry = push_button.geometry()
        height = geometry.height()
        desired_height = 32
        move = (height - desired_height) // 2
        geometry.setY(geometry.y() + move)
        geometry.setHeight(desired_height)
        push_button.setGeometry(geometry)
        push_button.setFixedHeight(desired_height)


def set_width_based_on_text_length(line_edit: QtWidgets.QLineEdit, minimal_text: str = '', horizontal_margin: int = 8):
    """
    Sets width of a line edit widget based on its text.

    Reference:
      https://stackoverflow.com/questions/48031291/adjusting-the-width-of-qlineedit-to-contents-and-getting-shorter-than-expected
    """
    font_metrics = QtGui.QFontMetrics(line_edit.font())
    text_width = font_metrics.boundingRect(line_edit.text()).width()
    minimal_text_width = font_metrics.boundingRect(minimal_text).width()
    text_width = max(text_width, minimal_text_width)
    line_edit.setFixedWidth(text_width + 2 * horizontal_margin)


def open_browser(url: str):
    url = QUrl(url)
    QDesktopServices.openUrl(url)
