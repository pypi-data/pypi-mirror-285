from enum import Enum
from functools import lru_cache
from typing import Optional, Tuple

from PyQt6.QtCore import Qt, QRect, QModelIndex
from PyQt6.QtGui import QPainter, QAbstractTextDocumentLayout, QTextDocument, QPalette, QColor
from PyQt6.QtWidgets import QComboBox, QProxyStyle, QStyle, QWidget, QStyleOptionComboBox

from tons.ui.gui.utils import macos, qt_exc_handler, blended_hint_color, windows, blended_text_color, \
    html_text_colored


class _MyComboBoxProxyStyle(QProxyStyle):
    @qt_exc_handler
    def drawComplexControl(self, control: QStyle.ComplexControl, option: Optional['QStyleOptionComplex'],
                           painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:
        if macos():
            option.rect.setX(option.rect.x() - 5)
            option.rect.setY(option.rect.y() + 2)
            option.rect.setWidth(option.rect.width() + 5)
        super().drawComplexControl(control, option, painter, widget)


class MyComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(_MyComboBoxProxyStyle())


@lru_cache
def _hint_color() -> str:
    if macos():
        return blended_text_color(0.15, background_role=QPalette.ColorRole.AlternateBase).name()
    return blended_hint_color().name()


class RichComboDataRole(Enum):
    hint = Qt.ItemDataRole.UserRole + 1  # v3r2  (Default)
                                         #       ^^^^^^^^^
    data = Qt.ItemDataRole.UserRole + 2  # v3r2  (Default)
                                         # ^^^^


def _data_with_hint(data: str, hint: str, plain: bool = False) -> str:
    if plain:
        return f'{data}  {hint}'
    return data + '  ' + html_text_colored(hint, _hint_color())


class _RichComboBoxProxyStyle(_MyComboBoxProxyStyle):
    @qt_exc_handler
    def drawControl(self, element: QStyle.ControlElement, option: Optional['QStyleOption'],
                    painter: Optional[QPainter], widget: Optional[QWidget] = ...) -> None:

        if element == QStyle.ControlElement.CE_ComboBoxLabel:

            assert isinstance(option, QStyleOptionComboBox)
            assert isinstance(widget, RichComboBox)

            current_index = widget.index_of_current_text()
            current_text = self._rich_text_with_hint(
                self._item_data(current_index),
                self._item_hint(current_index)
            )

            self._draw_selected_text_label(current_text, painter, option)
            return

        super().drawControl(element, option, painter, widget)

    def _rich_text_with_hint(self, text: str, hint: str):
        return _data_with_hint(text, hint)

    def _item_data(self, item_index: QModelIndex) -> str:
        return item_index.data(RichComboDataRole.data.value) or ''

    def _item_hint(self, item_index: QModelIndex) -> str:
        return item_index.data(RichComboDataRole.hint.value) or ''

    def _draw_selected_text_label(self, html_text: str, painter: QPainter, option: QStyleOptionComboBox):
        doc = self._document(html_text)
        text_rect = self._text_rect(option)
        self._draw_doc_in_rect(painter, doc, text_rect)

    def _draw_doc_in_rect(self, painter: QPainter, doc: QTextDocument, text_rect: QRect):
        ctx = QAbstractTextDocumentLayout.PaintContext()

        painter.save()
        painter.translate(text_rect.topLeft())
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def _document(self, html_text: str) -> QTextDocument:
        doc = QTextDocument()
        doc.setDocumentMargin(0)
        doc.setHtml(html_text)
        return doc

    def _text_rect(self, option: QStyleOptionComboBox):
        text_rect = option.rect
        margin_dx, margin_dy = self._combo_label_margins()
        text_rect.translate(margin_dx, margin_dy)
        return text_rect

    def _combo_label_margins(self) -> Tuple[int, int]:
        if windows():
            return 5, 2
        return 15, 0


class RichComboBox(MyComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(_RichComboBoxProxyStyle())

    def row_of_current_text(self) -> int:
        for i in range(self.count()):
            if self.itemText(i) == self.currentText():
                return i
        return -1

    def index_of_current_text(self) -> QModelIndex:
        current_index = self.view().model().index(self.row_of_current_text(), 0)
        return current_index

    def current_data(self) -> str:
        return self.index_of_current_text().data(RichComboDataRole.data.value)

    def add_item(self, data: str, hint: str = ''):
        idx = self.count()
        self.addItem(_data_with_hint(data, hint, plain=True))
        self.setItemData(idx, data, RichComboDataRole.data.value)
        self.setItemData(idx, hint, RichComboDataRole.hint.value)




