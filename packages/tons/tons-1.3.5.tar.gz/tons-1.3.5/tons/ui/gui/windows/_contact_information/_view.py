from typing import Protocol, List

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

from tons.ui.gui.uis import ContactInformationUI
from tons.ui.gui.utils import TextDisplayProperty, slot_exc_handler, ContactLocation, set_text_display_valid
from tons.ui.gui.utils import TonSymbolView
from .._base import NormalFixedSizeView
from ..components.whitelists import WhitelistsViewComponent
from ..mixins.entity_name import NameView, InvalidNameNotification
from ..mixins.last_activity import LastActivityView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView


class Presenter(Protocol):
    def on_copy_address(self): ...

    def on_copy_address_type_2(self): ...

    def on_copy_address_type_3(self): ...

    def on_copy_address_code(self): ...

    def on_copy_address_data(self): ...

    def on_show_qr_pressed(self): ...

    def on_viewmodel_updated(self): ...

    def on_save_clicked(self): ...

    def on_address_edited(self): ...

    def on_whitelist_changed(self, location: ContactLocation): ...


class ContactNameView(NameView):
    def _invalid_name_notification_text(self, kind: InvalidNameNotification):
        if kind == InvalidNameNotification.exists:
            return "Another contact with this name already exists"
        return super()._invalid_name_notification_text(kind)


class ContactInformationView(NormalFixedSizeView, ContactNameView, SaveCancelButtonBoxView, LastActivityView):
    contact_name = TextDisplayProperty('lineEditName')
    balance = TextDisplayProperty('labelBalanceTon')
    balance_fiat = TextDisplayProperty('labelBalanceFiat')
    default_message = TextDisplayProperty('lineEditDefaultMessage')
    workchain = TextDisplayProperty('labelWorkchainValue')

    address = TextDisplayProperty('lineEditAddress')

    def __init__(self):
        super().__init__(ContactInformationUI)
        self._advanced_options_block.setVisible(False)
        self._different_whitelist_selected = False
        self.init_name_view(self._name_validation_error_label, self._line_edit_name)
        self.init_button_box(self)
        self.ton_symbol = TonSymbolView(self._label_ton_icon)

        self._setup_signals()
        # self._stacked_widget_advanced_options.setCurrentIndex(1)
        self.whitelists = WhitelistsViewComponent(self._combo_box_whitelist)

    def _setup_signals(self):
        self._push_button_show_advanced_options.clicked.connect(self._on_show_advanced_options)

    def setup_signals(self, presenter: Presenter):
        self._push_button_qr.clicked.connect(presenter.on_show_qr_pressed)

        for line_edit in (self._line_edit_name, self._line_edit_default_message, self._line_edit_address):
            line_edit.textEdited.connect(presenter.on_viewmodel_updated)
        self.whitelists.changed.connect(self._on_location_changed)
        self.whitelists.changed.connect(presenter.on_whitelist_changed)
        self._line_edit_address.textEdited.connect(presenter.on_address_edited)

        self._push_button_copy_address.clicked.connect(presenter.on_copy_address)
        self._push_button_copy_address_type_2.clicked.connect(presenter.on_copy_address_type_2)
        self._push_button_copy_address_type_3.clicked.connect(presenter.on_copy_address_type_3)
        self._push_button_copy_address_code.clicked.connect(presenter.on_copy_address_code)
        self._push_button_copy_address_data.clicked.connect(presenter.on_copy_address_data)

        self._save_button.clicked.connect(presenter.on_save_clicked)

    def set_additional_address(self, address: str, idx: int):
        line_edit = self._line_edits_additional_addresses[idx]
        line_edit.setVisible(True)
        line_edit.setText(address)

        push_button = self._buttons_copy_additional_addresses[idx]
        push_button.setVisible(True)

    def set_additional_address_label(self, text: str, idx: int):
        label = self._labels_additional_addresses[idx]
        label.setText(text)

    def hide_additional_addresses(self):
        for line_edit in self._line_edits_additional_addresses:
            line_edit.setVisible(False)
        for label in self._labels_additional_addresses:
            label.setText('--')
        for push_button in self._buttons_copy_additional_addresses:
            push_button.setVisible(False)

    @pyqtSlot(ContactLocation)
    @slot_exc_handler()
    def _on_location_changed(self, contact_location: ContactLocation):
        self._line_edit_name.set_icon(self.whitelists.get_icon_path(contact_location))

    @property
    def address_type_2(self) -> str:
        return self._line_edit_address_type_2.text()

    @property
    def address_type_3(self) -> str:
        return self._line_edit_address_type_3.text()

    @property
    def _line_edits_additional_addresses(self) -> List[QLineEdit]:
        return [self._line_edit_address_type_2, self._line_edit_address_type_3]

    @property
    def _labels_additional_addresses(self) -> List[QLabel]:
        return [self._label_address_type_2, self._label_address_type_3]

    @property
    def _buttons_copy_additional_addresses(self) -> List[QPushButton]:
        return [self._push_button_copy_address_type_2, self._push_button_copy_address_type_3]

    @property
    def _combo_box_whitelist(self) -> QtWidgets.QComboBox:
        return self._ui.comboBoxWhitelist

    @property
    def _name_validation_error_label(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _line_edit_name(self) -> QLineEdit:
        return self._ui.lineEditName

    @property
    def _line_edit_default_message(self) -> QLineEdit:
        return self._ui.lineEditDefaultMessage

    @property
    def _line_edit_address(self) -> QLineEdit:
        return self._ui.lineEditAddress

    @property
    def _line_edit_address_type_2(self) -> QLineEdit:
        return self._ui.lineEditAddressType2

    @property
    def _line_edit_address_type_3(self) -> QLineEdit:
        return self._ui.lineEditAddressType3

    @property
    def _label_address_type_2(self) -> QLabel:
        return self._ui.labelAddressType2

    @property
    def _label_last_activity_value_date(self) -> QLabel:
        return self._ui.labelLastActivityValueDate

    @property
    def _label_last_activity_value_time(self) -> QLabel:
        return self._ui.labelLastActivityValueTime

    @property
    def _label_address_type_3(self) -> QLabel:
        return self._ui.labelAddressType3

    @property
    def _push_button_qr(self) -> QPushButton:
        return self._ui.pushButtonQR

    @property
    def _push_button_copy_address(self) -> QPushButton:
        return self._ui.pushButtonCopyAddress

    @property
    def _push_button_copy_address_type_2(self) -> QPushButton:
        return self._ui.pushButtonCopyAddressType2

    @property
    def _push_button_copy_address_type_3(self) -> QPushButton:
        return self._ui.pushButtonCopyAddressType3

    @property
    def _push_button_copy_address_code(self) -> QPushButton:
        return self._ui.pushButtonCopySharpAddressCode

    @property
    def _push_button_copy_address_data(self) -> QPushButton:
        return self._ui.pushButtonCopyAddressData

    @property
    def _push_button_show_advanced_options(self) -> QPushButton:
        return self._ui.toolButtonShowAdvancedOptions

    @property
    def _line(self) -> QWidget:
        return self._ui.line

    @property
    def _label_location(self) -> QLabel:
        return self._ui.labelLocation

    @property
    def _label_ton_icon(self) -> QLabel:
        return self._ui.labelTonIcon

    @property
    def _label_address_validation_error(self) -> QLabel:
        return self._ui.labelAddressValidationError

    @property
    def _more_options_button_block(self) -> QWidget:
        return self._ui.moreOptionsButtonBlock

    @property
    def _advanced_options_block(self) -> QWidget:
        return self._ui.moreOptionsRevealedWidgetBlock

    @pyqtSlot()
    @slot_exc_handler()
    def _on_show_advanced_options(self):
        self._more_options_button_block.hide()
        self._advanced_options_block.setVisible(True)

    def notify_viewmodel_different(self):
        self._save_button.setDisabled(False)

    def notify_viewmodel_unchanged(self):
        self._save_button.setDisabled(True)

    def notify_address_already_exists(self, name: str):
        message = f"Contact with this address already exists: <b>{name}</b>"
        self._label_address_validation_error.setText(message)
        self._label_address_validation_error.setVisible(True)
        set_text_display_valid(self._line_edit_address, False)

    def notify_address_invalid(self):
        self._label_address_validation_error.setText("Invalid address")
        self._label_address_validation_error.setVisible(True)
        set_text_display_valid(self._line_edit_address, False)

    def notify_address_valid(self):
        set_text_display_valid(self._line_edit_address, True)
        self._label_address_validation_error.setVisible(False)

    def hide_input_error_notifications(self):
        self.hide_name_validation_error_notification()
