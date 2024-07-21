import decimal
from decimal import Decimal
from pathlib import Path
from typing import Protocol, Optional, Dict

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QToolButton, QWidget, QLineEdit, QPushButton, QLayout, QLabel, QCheckBox, QStackedWidget, \
    QFileDialog, QAbstractButton

from tons.ui.gui.services import ton_usd_price
from tons.ui.gui.uis import TransferUI
from tons.ui.gui.utils import slot_exc_handler, ton_balance_validator, TextDisplayProperty, set_text_display_valid, \
    xstr, pretty_fiat_balance
from tons.ui.gui.widgets import WalletListItemData, WalletListItemView, WalletListItemKind
from tons.ui.gui.windows._base import NormalFixedSizeView
from tons.ui.gui.windows.mixins.save_cancel_buttonbox import SaveCancelButtonBoxView


class Presenter(Protocol):
    def on_select_to_pressed(self): ...
    def on_select_from_pressed(self): ...
    def on_transfer_pressed(self): ...
    def on_check_box_transfer_all_state_changed(self, state: int): ...


class TransferView(NormalFixedSizeView, SaveCancelButtonBoxView):
    amount = TextDisplayProperty("lineEditAmount")
    message = TextDisplayProperty("lineEditComment")
    state_init_boc_path = TextDisplayProperty('lineEditStateInitBocPath')
    body_boc_path = TextDisplayProperty('lineEditBodyBocPath')

    def __init__(self):
        super().__init__(TransferUI)
        self._advanced_options_block.setVisible(False)
        self._setup_signals()

        validator = ton_balance_validator()
        self._line_edit_amount.setText('')
        self._line_edit_amount.setValidator(validator)

        self._wallet_list_item_widget_from: Optional[WalletListItemView] = None
        self._wallet_list_item_widget_to: Optional[WalletListItemView] = None

        self.init_button_box(self)

        self._amount_memo: str = ''

        self._button_text_memo = self._init_button_text_memo()

    def _init_button_text_memo(self) -> Dict[QAbstractButton, str]:
        memo = dict()
        for button in [self._button_select_wallet_to, self._button_select_wallet_from]:
            memo[button] = button.text()
        return memo

    def _restore_button_text(self, button: QPushButton):
        initial_text = self._button_text_memo[button]
        button.setText(initial_text)

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_amount.setFocus()

    def _setup_signals(self):
        self._button_show_advanced_options.clicked.connect(self._on_show_advanced_options_clicked)
        self._line_edit_amount.textEdited.connect(self._on_amount_edited)
        self._line_edit_amount.textChanged.connect(self._on_amount_changed)
        self._line_edit_comment.textChanged.connect(self._on_comment_changed)
        self._button_state_init_browse.clicked.connect(self._on_state_init_browse)
        self._button_body_browse.clicked.connect(self._on_body_browse)

    def setup_signals(self, presenter: Presenter):
        self._button_select_wallet_to.clicked.connect(presenter.on_select_to_pressed)
        self._button_select_wallet_from.clicked.connect(presenter.on_select_from_pressed)
        self._save_button.clicked.connect(presenter.on_transfer_pressed)
        self._check_box_transfer_all.stateChanged.connect(presenter.on_check_box_transfer_all_state_changed)

    def notify_wallet_from_not_selected(self):
        set_text_display_valid(self._widget_from, False)
        self._label_select_wallets_error.setText('Select sender and recipient')
        self._label_select_wallets_error.setVisible(True)

    def notify_wallet_from_balance_not_loaded(self):
        set_text_display_valid(self._widget_from, False)
        self._label_select_wallets_error.setText('Please, wait until the balance is loaded')
        self._label_select_wallets_error.setVisible(True)

    def notify_wallet_to_not_selected(self):
        set_text_display_valid(self._widget_to, False)
        self._label_select_wallets_error.setText('Select sender and recipient')
        self._label_select_wallets_error.setVisible(True)

    def notify_wallet_to_can_not_read_encrypted_messages(self):
        set_text_display_valid(self._widget_to, False)
        self._label_select_wallets_error.setText('This recipient can not read encrypted comments')
        self._label_select_wallets_error.setVisible(True)

    def hide_wallet_validity_notification(self):
        self._label_select_wallets_error.setVisible(False)

    # def notify_comment_invalid(self, error):
    #     set_text_display_valid(self._line_edit_comment, False)
    #     self._label_comment_error.setText(error)
    #     self._label_comment_error.setVisible(True)

    # def hide_comment_invalid(self):
    #     set_text_display_valid(self._line_edit_comment, True)
    #     self._label_comment_error.setVisible(False)

    def notify_amount_invalid(self):
        set_text_display_valid(self._line_edit_amount, False)

    def notify_state_init_path_invalid(self, error):
        set_text_display_valid(self._state_init_path_line_edit, False)
        self._label_state_init_error.setText(error)
        self._label_state_init_error.setVisible(True)

    def hide_state_init_path_validity_notification(self):
        set_text_display_valid(self._state_init_path_line_edit, True)
        self._label_state_init_error.setVisible(False)

    def notify_body_path_invalid(self, error):
        set_text_display_valid(self._body_path_line_edit, False)
        self._label_body_error.setText(error)
        self._label_body_error.setVisible(True)

    def hide_body_path_validity_notification(self):
        set_text_display_valid(self._body_path_line_edit, True)
        self._label_body_error.setVisible(False)

    def disable_amount_input(self):
        set_text_display_valid(self._line_edit_amount, True)
        self._line_edit_amount.setEnabled(False)
        self._line_edit_amount.setReadOnly(True)

    def enable_amount_input(self):
        self._line_edit_amount.setEnabled(True)
        self._line_edit_amount.setReadOnly(False)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_show_advanced_options_clicked(self):
        self._show_advanced_options()

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_amount_edited(self, text: str):
        set_text_display_valid(self._line_edit_amount, text != '')

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_amount_changed(self, text: str):
        try:
            fiat_amount = Decimal(text) * ton_usd_price()
        except (decimal.InvalidOperation, TypeError, ValueError):
            fiat_amount = None
        self._set_fiat_amount(fiat_amount)

    def _set_fiat_amount(self, fiat_amount: Optional[Decimal]):
        if fiat_amount is None:
            self._label_amount_fiat.setText('')
            return

        pretty_fiat_amount = '≈ ' + pretty_fiat_balance(fiat_amount, '$')  # todo refactor
        self._label_amount_fiat.setText(pretty_fiat_amount)

    @pyqtSlot(str)
    @slot_exc_handler()
    def _on_comment_changed(self, text: str):
        if text:
            self._check_box_encrypt_message.setEnabled(True)
        else:
            self._check_box_encrypt_message.setEnabled(False)
            self._check_box_encrypt_message.setChecked(False)


    @property
    def _button_show_advanced_options(self) -> QToolButton:
        return self._ui.toolButtonShowAdvancedOptions

    @property
    def _button_select_wallet_from(self) -> QToolButton:
        return self._ui.toolButtonWalletFrom

    @property
    def _button_select_wallet_to(self) -> QToolButton:
        return self._ui.toolButtonWalletTo

    @property
    def _button_state_init_browse(self) -> QPushButton:
        return self._ui.pushButtonStateInitBrowse

    @property
    def _button_body_browse(self) -> QPushButton:
        return self._ui.pushButtonBodyBrowse

    @property
    def _stacked_widget_advanced_options(self) -> QStackedWidget:
        return self._ui.stackedWidgetAdvancedOptions

    @property
    def _line_edit_amount(self) -> QLineEdit:
        return self._ui.lineEditAmount

    @property
    def _line_edit_comment(self) -> QLineEdit:
        return self._ui.lineEditComment

    @property
    def _widget_from(self) -> QWidget:
        return self._ui.widgetFrom

    @property
    def _widget_to(self) -> QWidget:
        return self._ui.widgetTo

    @property
    def _label_select_wallets_error(self) -> QLabel:
        return self._ui.labelErrorSelectWallets

    # @property
    # def _label_comment_error(self) -> QLabel:
    #     return self._ui.labelCommentValidationError

    @property
    def _label_state_init_error(self) -> QLabel:
        return self._ui.labelErrorStateInit

    @property
    def _label_body_error(self) -> QLabel:
        return self._ui.labelErrorBody

    @property
    def _label_amount_fiat(self) -> QLabel:
        return self._ui.labelAmountFiat

    @property
    def _check_box_encrypt_message(self) -> QCheckBox:
        return self._ui.checkBoxEncryptMessage

    @property
    def _check_box_transfer_all(self) -> QCheckBox:
        return self._ui.checkBoxTransferAll

    @property
    def _check_box_destroy_if_zero(self) -> QCheckBox:
        return self._ui.checkBoxDestroyIfZero

    @property
    def _more_options_button_block(self) -> QWidget:
        return self._ui.moreOptionsButtonBlock

    @property
    def _advanced_options_block(self) -> QWidget:
        return self._ui.moreOptionsRevealedWidgetBlock

    @property
    def _state_init_path_line_edit(self) -> QWidget:
        return self._ui.lineEditStateInitBocPath

    @property
    def _body_path_line_edit(self) -> QWidget:
        return self._ui.lineEditBodyBocPath

    @property
    def wallet_list_item_widget_from(self) -> WalletListItemView:
        layout = self._widget_from.layout()
        widget = self._get_wallet_list_item_widget(layout)
        return widget

    @property
    def wallet_list_item_widget_to(self) -> WalletListItemView:
        layout = self._widget_to.layout()
        widget = self._get_wallet_list_item_widget(layout)
        return widget

    @property
    def encrypt_message(self) -> bool:
        checkbox = self._check_box_encrypt_message
        return checkbox.isChecked()

    @encrypt_message.setter
    def encrypt_message(self, value: bool):
        self._check_box_encrypt_message.setChecked(value)

    @property
    def transfer_all_coins(self) -> bool:
        checkbox = self._check_box_transfer_all
        return checkbox.isChecked()

    @transfer_all_coins.setter
    def transfer_all_coins(self, value: bool):
        self._check_box_transfer_all.setChecked(value)

    @property
    def destroy_if_zero(self) -> bool:
        checkbox = self._check_box_destroy_if_zero
        return checkbox.isChecked()

    @destroy_if_zero.setter
    def destroy_if_zero(self, value: bool):
        self._check_box_destroy_if_zero.setChecked(value)

    def _get_wallet_list_item_widget(self, layout: QLayout) -> WalletListItemView:
        widget = self._get_layout_widget(layout)
        assert isinstance(widget, WalletListItemView)
        return widget

    def _show_advanced_options(self):
        self._more_options_button_block.hide()
        self._advanced_options_block.setVisible(True)

    def show_advanced_options(self):
        self._show_advanced_options()

    def _on_state_init_browse(self):
        path = self._on_browse('Select state init .boc file')
        if path:
            self.state_init_boc_path = path

    def _on_body_browse(self):
        path = self._on_browse('Select body .boc file')
        if path:
            self.body_boc_path = path

    def _on_browse(self, caption):
        filepath, _ = QFileDialog.getOpenFileName(parent=self, caption=caption)
        if filepath != '':
            filepath = Path(filepath)
            filepath = str(filepath)
        return filepath

    def display_wallet_from(self, wallet: Optional[WalletListItemData]):
        layout = self._widget_from.layout()
        button = self._button_select_wallet_from
        self._display_wallet(wallet, layout, button)

        set_text_display_valid(self._widget_from, True)

    def display_wallet_to(self, wallet: Optional[WalletListItemData]):
        set_text_display_valid(self._widget_to, True)
        layout = self._widget_to.layout()
        button = self._button_select_wallet_to
        self._display_wallet(wallet, layout, button)
        set_text_display_valid(self._widget_to, True)

    def display_default_transfer_message(self, wallet: Optional[WalletListItemData]):
        if wallet is None:
            self.message = ''
            return
        if wallet.kind in [WalletListItemKind.local_contact, WalletListItemKind.global_contact]:
            self.message = xstr(wallet.comment)

    def _display_wallet(self, wallet: Optional[WalletListItemData], layout: QLayout, button: QPushButton):
        wallet_widget = self._get_layout_widget(layout)
        if wallet is not None:
            wallet_widget.display_model(wallet)
            button.setText('')
        else:
            layout.removeWidget(wallet_widget)
            self._restore_button_text(button)

    @staticmethod
    def _get_layout_widget(layout: QLayout) -> WalletListItemView:
        layout_item = layout.itemAt(0)
        try:
            widget = layout_item.widget()
            assert isinstance(widget, WalletListItemView)
        except AttributeError:
            wallet_widget = WalletListItemView()
            layout.addWidget(wallet_widget)
            return wallet_widget
        else:
            return widget
