from typing import Optional

from PyQt6.QtCore import QRect, QSize, QObject, QEvent, Qt, pyqtSlot
from PyQt6.QtGui import QPalette, QColor, QPainter, QPen
from PyQt6.QtWidgets import QPlainTextEdit, QProxyStyle, QStyleOption, QStyle, QWidget, QApplication

from tons.ui.gui.utils import line_edit_border_color, macos, windows, very_valid_color, validation_error_color, \
    qt_exc_handler, text_document_blocks, slot_exc_handler


# TODO refactor DRY (MyLineEdit)


def _pick_border_color(line_edit: 'MyPlainTextEdit') -> QColor:
    """ Very-validity has been disabled by the UX designer's will """
    # if line_edit.text_very_valid():
    #     return very_valid_color()
    if not line_edit.text_valid():
        return validation_error_color()
    elif line_edit.hasFocus():
        return line_edit.palette().color(QPalette.ColorRole.Highlight)
    else:
        return line_edit_border_color()


def _needs_colorful_border(widget: 'MyPlainTextEdit') -> bool:
    return widget.hasFocus()


def _pick_width(widget: 'MyPlainTextEdit') -> int:
    if macos():
        if _needs_colorful_border(widget):
            return 4
    return 2


def _needs_override_default_border(widget: 'MyPlainTextEdit') -> bool:
    if macos():
        return True
    if _needs_colorful_border(widget):
        return True
    return False


def _draw_border(rect: QRect, widget: 'MyPlainTextEdit', painter: QPainter):
    color = _pick_border_color(widget)
    width = _pick_width(widget)
    pen = QPen(color)
    pen.setWidth(width)
    painter.setPen(pen)
    if windows():
        rect.setRight(rect.right() - 1)
        rect.setBottom(rect.bottom() - 1)
    painter.drawRect(rect)


class MyPlainTextStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        assert isinstance(widget, MyPlainTextEdit)
        if element != QStyle.ControlElement.CE_ShapedFrame or (not _needs_override_default_border(widget)):
            super().drawControl(element, option, painter, widget)
        _draw_border(option.rect, widget, painter)

    @qt_exc_handler
    def subElementRect(self, element: QStyle.SubElement, option: Optional['QStyleOption'],
                       widget: Optional[QWidget]) -> QRect:
        """ TODO: set individual sizes for subelements """
        rect = super().subElementRect(element, option, widget)

        margin = 1

        rect.setLeft(rect.left() + margin)
        rect.setRight(rect.right() - margin)
        rect.setTop(rect.top() + margin)
        rect.setBottom(rect.bottom() - margin)

        return rect


class MyPlainTextEdit(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(MyPlainTextStyle())
        self.__text_valid = True
        self.__text_very_valid = False

    def set_text_valid(self, valid: bool):
        self.__text_valid = valid

    def text_valid(self) -> bool:
        return self.__text_valid

    def set_text_very_valid(self, very_valid: bool):
        self.__text_very_valid = very_valid

    def text_very_valid(self) -> bool:
        return self.__text_very_valid

    @qt_exc_handler
    def setStyleSheet(self, _: Optional[str]) -> None:
        assert False


class MnemonicsPlainTextEditEditable(MyPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installEventFilter(self)
        self.textChanged.connect(self._on_text_changed)

    @pyqtSlot()
    @slot_exc_handler
    def _on_text_changed(self):
        self._set_height_based_on_contents()

    def _set_height_based_on_contents(self):
        self.setFixedHeight(self._adaptive_height())

    def _adaptive_height(self) -> int:
        """
        For some reason the self.document().size() function returns number of lines instead of actual pixel height.
        Qt is a weirdo.
        https://stackoverflow.com/questions/45028105/get-the-exact-height-of-qtextdocument-in-pixels
        """
        doc = self.document()
        layout = doc.documentLayout()
        adaptive_height = sum(layout.blockBoundingRect(block).height() for block in text_document_blocks(doc))
        adaptive_height = int(adaptive_height + doc.documentMargin() + 2 * self.frameWidth() + 1)
        return adaptive_height


    @qt_exc_handler
    def eventFilter(self, obj: Optional[QObject], event: Optional[QEvent]) -> bool:
        if obj == self and \
            event.type() == QEvent.Type.KeyPress and \
            event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:

            return True

        return False
