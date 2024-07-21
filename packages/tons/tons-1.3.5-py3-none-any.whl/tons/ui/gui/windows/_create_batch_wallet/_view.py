from typing import Protocol, Sequence, Optional, Any, Tuple

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QLabel, QComboBox, QDialogButtonBox, QPushButton, QWidget, QLineEdit

from tons.ui.gui.uis import CreateBatchWalletUI
from tons.ui.gui.utils import TextDisplayProperty, show_message_box_warning, slot_exc_handler, \
    set_width_based_on_text_length
from ._utils import range_decimal_places, range_is_valid
from .._base import NormalView, NormalFixedSizeView
from ..mixins.keystore_selection import KeystoreSelectView
from ..mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from ..mixins.wallet_version_selection import WalletVersionSelectView
from ..mixins.workchain_selection import WorkchainSelectView
from ...utils import set_text_display_valid


class Presenter(Protocol):
    def on_save_clicked(self): ...
    def on_pattern_changed(self): ...
    def on_keystore_changed(self, name: str): ...


class CreateBatchWalletView(NormalFixedSizeView, KeystoreSelectView, WalletVersionSelectView, WorkchainSelectView,
                            SaveCancelButtonBoxView):
    _from_idx = TextDisplayProperty('lineEditFrom')
    _to_idx = TextDisplayProperty('lineEditTo')
    prefix = TextDisplayProperty('lineEditNameLeft')
    _sample_count = TextDisplayProperty('lineEditSampleCount')
    suffix = TextDisplayProperty('lineEditNameRight')
    comment = TextDisplayProperty('lineEditComment')
    explanation = TextDisplayProperty('labelPatternDescription')

    def __init__(self):
        super().__init__(CreateBatchWalletUI)
        self.default_explanation = self.explanation
        self._default_sample_count = self.sample_count

        self._setup_signals()
        self.setup_validators()
        self.hide_validation_errors()

        self.init_keystore_select_view()
        self.init_button_box(self)

    def setFocus(self) -> None:
        super().setFocus()
        self._line_edit_from.setFocus()

    def _setup_signals(self):
        self._line_edit_prefix.textEdited.connect(self._on_prefix_edited)
        self._line_edit_suffix.textEdited.connect(self._on_suffix_edited)
        self._line_edit_from.textEdited.connect(self._on_range_edited)
        self._line_edit_to.textEdited.connect(self._on_range_edited)

    def setup_signals(self, presenter: Presenter):
        self._save_button.pressed.connect(presenter.on_save_clicked)
        for widget in (self._line_edit_prefix,
                       self._line_edit_suffix,
                       self._line_edit_from,
                       self._line_edit_to):
            widget.textEdited.connect(presenter.on_pattern_changed)
        self._keystore_changed.connect(presenter.on_keystore_changed)

    def setup_validators(self):
        validator = QIntValidator()
        self._line_edit_from.setValidator(validator)
        self._line_edit_to.setValidator(validator)

    @property
    def from_idx(self) -> Optional[int]:
        try:
            return int(self._from_idx)
        except ValueError:
            return None

    @property
    def to_idx(self) -> Optional[int]:
        try:
            return int(self._to_idx)
        except ValueError:
            return None

    @property
    def sample_count(self) -> str:
        return self._sample_count

    @sample_count.setter
    def sample_count(self, value: str):
        self._sample_count = value
        set_width_based_on_text_length(self._line_edit_sample, minimal_text='###')
        w: QWidget = self._ui.namePatternBlock
        w.layout().update()

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
    def _line_edit_from(self) -> QLineEdit:
        return self._ui.lineEditFrom

    @property
    def _line_edit_to(self) -> QLineEdit:
        return self._ui.lineEditTo

    @property
    def _line_edit_prefix(self) -> QLineEdit:
        return self._ui.lineEditNameLeft

    @property
    def _line_edit_suffix(self) -> QLineEdit:
        return self._ui.lineEditNameRight

    @property
    def _line_edit_sample(self) -> QLineEdit:
        return self._ui.lineEditSampleCount

    @property
    def _label_validation_error(self) -> QLabel:
        return self._ui.labelNameValidationError

    @property
    def _label_validation_block(self) -> QWidget:
        return self._ui.nameValidationBlock

    @property
    def _editable_line_edits(self) -> Tuple[QLineEdit, ...]:
        return self._line_edit_to, self._line_edit_from, self._line_edit_prefix, self._line_edit_suffix

    @pyqtSlot()
    @slot_exc_handler()
    def _on_prefix_edited(self):
        set_text_display_valid(self._line_edit_prefix, True)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_suffix_edited(self):
        set_text_display_valid(self._line_edit_suffix, True)

    @pyqtSlot()
    @slot_exc_handler()
    def _on_range_edited(self):
        self._notify_range_valid_if_valid()

    def _notify_range_valid_if_valid(self):
        try:
            if self.from_idx < self.to_idx:
                set_text_display_valid(self._line_edit_from, True)
                set_text_display_valid(self._line_edit_to, True)
        except TypeError:
            pass

    def display_sample_count(self):
        if not range_is_valid(self.from_idx, self.to_idx):
            self.sample_count = "###"
            return
        template = f"%0{range_decimal_places(self.from_idx, self.to_idx)}d"
        self.sample_count = template % self.from_idx

    def notify_bad_range(self):
        if self.from_idx is None or (self.to_idx is not None and self.to_idx < self.from_idx):
            set_text_display_valid(self._line_edit_from, False)
        if self.to_idx is None or (self.from_idx is not None and self.to_idx < self.from_idx):
            set_text_display_valid(self._line_edit_to, False)
        self.display_validation_error("Bad range!")

    @staticmethod
    def notify_address_already_exists(name: str, address: str):
        title = "Record already exists"
        message = f"Rare unexpected collision happened. Wallet with address \n" \
                  f"{address} already exists: \n" \
                  f"{name}. Please retry."
        show_message_box_warning(title, message)

    def notify_name_exists(self):
        message = 'Oops, record with one of the generated wallet names already exists!'
        for widget in self._editable_line_edits:
            set_text_display_valid(widget, False)
        self.display_validation_error(message)

    def hide_validation_errors(self):
        self._label_validation_block.hide()
        self._label_validation_error.setVisible(True)

    def display_validation_error(self, text: str):
        self._label_validation_error.setText(text)
        self._label_validation_block.show()

    def remove_validation_error(self):
        self._label_validation_error.setText("")
        self._label_validation_block.hide()


__all__ = ['CreateBatchWalletView']


