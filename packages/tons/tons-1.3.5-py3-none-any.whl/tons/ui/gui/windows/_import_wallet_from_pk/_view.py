from typing import Protocol, Optional, List

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PyQt6.QtWidgets import QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, QWidget

from tons.ui.gui.uis import ImportWalletFromPrivateKeyUI
from tons.ui.gui.utils import TextDisplayProperty, show_message_box_warning, slot_exc_handler, qt_exc_handler
from .._base import NormalFixedSizeView
from ..components.entity_name import InvalidNameNotification
from tons.ui.gui.utils import TonSymbolView
from ..mixins.keystore_selection import KeystoreSelectView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from ..mixins.entity_name import NameView
from ..mixins.wallet_version_selection import WalletVersionSelectView
from ..mixins.workchain_selection import WorkchainSelectView
from ...promoted_widgets import DropPkLabel


class Presenter(Protocol):
    def on_user_changed_wallet_info(self): ...
    def on_keystore_changed(self, new_name: str): ...
    def on_save_clicked(self): ...

    def on_pk_path_selected(self, pk_path: str): ...


class WalletNameView(NameView):
    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another wallet with this name already exists"
        return NameView._invalid_name_notification_text(kind)


class ImportWalletFromPrivateKeyView(NormalFixedSizeView, WalletNameView, KeystoreSelectView, WalletVersionSelectView, WorkchainSelectView,
                                    SaveCancelButtonBoxView):
    _BROWSE_CAPTION = 'Browse...'
    _BROWSE_AGAIN_CAPTION = 'Browse other...'

    wallet_name = TextDisplayProperty('lineEditName')
    balance = TextDisplayProperty('labelBalanceTon')
    balance_fiat = TextDisplayProperty('labelBalanceFiat')
    comment = TextDisplayProperty('lineEditComment')
    _pk_path = TextDisplayProperty('labelPkFileName')

    _sig_pk_path_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__(ImportWalletFromPrivateKeyUI)
        self.init_name_view(self._name_validation_error_label, self._line_edit_name)
        self.init_keystore_select_view()
        self.init_button_box(self)
        self.ton_symbol = TonSymbolView(self._label_ton_icon)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self._unmake_window_drop_receiver()
        self._name_edited = False

    @property
    def name_edited(self) -> bool:
        return self._name_edited

    @qt_exc_handler
    def dragEnterEvent(self, event: QDragEnterEvent):
        event.acceptProposedAction()
        self._make_window_drop_receiver()

    @qt_exc_handler
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.releaseMouse()  # TODO ?
        self._unmake_window_drop_receiver()

    @qt_exc_handler
    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return

        urls = mime_data.urls()
        if len(urls) != 1:
            return

        url = urls[0]
        if not url.isLocalFile():
            return

        event.acceptProposedAction()

        local_file_path = url.toLocalFile()
        self._sig_pk_path_selected.emit(local_file_path)

        self._unmake_window_drop_receiver()

    @qt_exc_handler
    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_name.setFocus()

    def setup_signals(self, presenter: Presenter):
        self._combo_box_workchain.currentTextChanged.connect(presenter.on_user_changed_wallet_info)
        self._combo_box_version.currentTextChanged.connect(presenter.on_user_changed_wallet_info)
        self._save_button.pressed.connect(presenter.on_save_clicked)
        self._keystore_changed.connect(presenter.on_keystore_changed)
        self._push_button_browse.clicked.connect(self._on_browse_clicked)
        self._label_drop_pk_here.clicked.connect(self._on_browse_clicked)
        self._sig_pk_path_selected.connect(presenter.on_pk_path_selected)
        self._line_edit_name.textEdited.connect(self._on_name_edited)

        """ Button box """
        self._cancel_button.clicked.connect(self.close)

    def _init_browse_button(self):
        self._push_button_browse.setText(self._BROWSE_CAPTION)

    def _set_browse_button_file_selected(self):
        self._push_button_browse.setText(self._BROWSE_AGAIN_CAPTION)

    @property
    def pk_path(self) -> str:
        return self._pk_path

    @pk_path.setter
    def pk_path(self, pk_path: Optional[str]):
        if not pk_path:
            self._set_pk_path_none()
        else:
            self._set_pk_path(pk_path)

    def _set_pk_path_none(self):
        self._pk_path = ''
        self._label_pk_file_name.hide()
        self._init_browse_button()
        self._show_drop_pk_message()

    def _show_drop_pk_message(self):
        self._label_drop_pk_here.show()
        self._label_or_pk.show()
        self._spacer_drop_pk.hide()

    def _set_pk_path(self, pk_path: str):
        self._pk_path = pk_path
        self._label_pk_file_name.show()
        self._set_browse_button_file_selected()
        self._hide_drop_pk_message()


    def _hide_drop_pk_message(self):
        self._label_drop_pk_here.hide()
        self._label_or_pk.hide()
        self._spacer_drop_pk.show()

    def _root_widgets(self) -> List[QWidget]:
        names = ['advancedBlock_4', 'bottomBlock', 'commentBlock', 'line', 'nameBlock', 'nameValidationBlock', 'pkBlock']
        return [getattr(self._ui, widget_name) for widget_name in names]

    def _make_window_drop_receiver(self):
        # m = self.layout().contentsMargins()
        # minw = self.width() - m.left() - m.right()
        # minh = self.height() - m.top() - m.bottom()
        # self._label_drop_pk_here_big.setMinimumSize(minw, minh)

        for widget in self._root_widgets():
            widget.hide()
        self._label_drop_pk_here_big.show()

    def _unmake_window_drop_receiver(self):
        self._label_drop_pk_here_big.hide()
        for widget in self._root_widgets():
            widget.show()

    @pyqtSlot()
    @slot_exc_handler()
    def _on_browse_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                "Select private key file")
        if file_path:
            self._sig_pk_path_selected.emit(file_path)

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_name_edited(self, txt):
        self._name_edited = True


    @property
    def _combo_box_keystore(self) -> QComboBox:
        return self._ui.comboBoxKeystore

    @property
    def _combo_box_version(self) -> QComboBox:
        return self._ui.comboBoxVersion

    @property
    def _combo_box_workchain(self) -> QComboBox:
        return self._ui.comboBoxWorkchain

    @property
    def _name_validation_error_label(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _label_ton_icon(self) -> QLabel:
        return self._ui.labelTonIcon

    @property
    def _label_drop_pk_here(self) -> DropPkLabel:
        return self._ui.labelDropPkFileHere

    @property
    def _label_drop_pk_here_big(self) -> DropPkLabel:
        return self._ui.labelDropPkFileHere_2

    @property
    def _spacer_drop_pk(self) -> QWidget:
        return self._ui.widgetSpacerPk

    @property
    def _label_or_pk(self) -> QLabel:
        return self._ui.labelOrPk

    @property
    def _label_pk_file_name(self) -> QLabel:
        return self._ui.labelPkFileName

    @property
    def _push_button_browse(self) -> QPushButton:
        return self._ui.pushButtonBrowse

    @staticmethod
    def notify_address_already_exists(name: str):
        title = "Record already exists"
        message = f"Wallet with this address already exists: \n{name}"
        show_message_box_warning(title, message)

    @staticmethod
    def notify_invalid_pk(additional_info: str = ''):
        title = "Invalid private key"
        message = f"Invalid private key"
        if additional_info:
            message += ': ' + additional_info
        show_message_box_warning(title, message)


__all__ = ['ImportWalletFromPrivateKeyView']


