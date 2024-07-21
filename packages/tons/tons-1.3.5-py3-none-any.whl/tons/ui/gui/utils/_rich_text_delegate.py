# from typing import Optional
#
# from PyQt6 import QtGui
# from PyQt6.QtCore import QModelIndex, Qt, QSize
# from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
#
# from tons.ui.gui.utils import qt_exc_handler
#
#
# class RichTextDelegate(QStyledItemDelegate):
#     """
#     References:
#         https://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt
#     """
#     @qt_exc_handler
#     def paint(self, painter: Optional[QtGui.QPainter], option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
#         options = QStyleOptionViewItem(option)
#         self.initStyleOption(options, index)
#         style = options.widget.style()
#
#         doc = self.get_document(options, index)
#
#         style.drawControl(QStyle.ControlElement.CE_ItemViewItem, options, painter)
#
#         ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
#
#         text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options)
#         painter.save()
#         painter.translate(text_rect.topLeft())
#         painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
#         doc.documentLayout().draw(painter, ctx)
#
#         painter.restore()
#
#     def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
#         options = QStyleOptionViewItem(option)
#         self.initStyleOption(options, index)
#         doc = self.get_document(options, index)
#         return QSize(int(doc.idealWidth()), int(doc.size().height()))
#
#     def get_document(self, options: QStyleOptionViewItem, index: QModelIndex):
#         html_to_display = options.text
#         data = index.data(Qt.ItemDataRole.UserRole)
#         if data is not None:
#             html_to_display += f' <font color=gray>{data}</font>'
#
#         doc = QtGui.QTextDocument()
#         doc.setHtml(html_to_display)
#         options.text = ""
#         return doc
