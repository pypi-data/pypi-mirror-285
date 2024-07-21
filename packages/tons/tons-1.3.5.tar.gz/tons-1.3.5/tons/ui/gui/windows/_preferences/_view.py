from functools import lru_cache
from pathlib import Path
from typing import Protocol

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QComboBox, QSlider, QLineEdit, QPushButton, QFileDialog, QLabel

from tons.ui._utils import dns_expire_soon_threshold
from tons.ui.gui.uis import PreferencesUI
from tons.ui.gui.utils import TextDisplayProperty, set_text_display_valid, ton_balance_validator, html_text_colored
from tons.ui.gui.windows._base import NormalFixedSizeView
from tons.ui.gui.windows.mixins.save_cancel_buttonbox import SaveCancelButtonBoxView
from tons.ui.gui.windows.mixins.wallet_version_selection import WalletVersionSelectView


@lru_cache
def _until_color() -> QColor:
    return QColor(0x80, 0x80, 0x80)


class Presenter(Protocol):
    def on_viewmodel_updated(self): ...
    def on_save(self): ...
    def on_restore_defaults(self): ...


class PreferencesView(NormalFixedSizeView, WalletVersionSelectView, SaveCancelButtonBoxView):
    user_directory = TextDisplayProperty('lineEditUserDirectory')
    api_key = TextDisplayProperty('lineEditApiKey')
    testnet_api_key = TextDisplayProperty('lineEditTestnetApiKey')
    dns_refresh_amount = TextDisplayProperty('lineEditDnsRefreshAmount')
    jetton_gas_amount = TextDisplayProperty('lineEditJettonGasAmount')

    _dns_expiring_in_verbose = TextDisplayProperty('labelDnsExpiringIn')

    def __init__(self):
        super().__init__(PreferencesUI)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._setup_signals()
        self._setup_validators()
        self.init_button_box(self)
        self._on_slider_changed()
        self._hide_hidden_features()

    def setFocus(self) -> None:
        if not any([self.api_key, self.testnet_api_key]):
            self.focus_on_api_key()


    def _hide_hidden_features(self):
        self._button_restore_defaults.hide()

    def setup_signals(self, presenter: Presenter):
        for line_edit in (
            self._line_edit_user_directory,
            self._line_edit_api_key,
            self._line_edit_testnet_api_key,
            self._line_edit_dns_refresh_amount,
            self._line_edit_jetton_gas_amount
        ):
            line_edit.textChanged.connect(presenter.on_viewmodel_updated)

        for combo in (
            self._combo_box_version,
            self._combo_box_network,
            self._combo_box_scanner
        ):
            combo.currentIndexChanged.connect(presenter.on_viewmodel_updated)

        self._slider_dns.valueChanged.connect(presenter.on_viewmodel_updated)
        self._save_button.clicked.connect(presenter.on_save)
        self._button_restore_defaults.clicked.connect(presenter.on_restore_defaults)

    def _setup_signals(self):
        self._slider_dns.valueChanged.connect(self._on_slider_changed)
        self._button_browse.clicked.connect(self._on_browse)
        self._line_edit_dns_refresh_amount.textEdited.connect(self._on_dns_refresh_amount_edited)
        self._line_edit_jetton_gas_amount.textEdited.connect(self._on_jetton_amount_edited)

    def _setup_validators(self):
        validator = ton_balance_validator()
        self._line_edit_dns_refresh_amount.setValidator(validator)
        self._line_edit_jetton_gas_amount.setValidator(validator)

    @property
    def network(self) -> str:
        return self._combo_box_network.currentText()

    @network.setter
    def network(self, network: str):
        combo_values = [self._combo_box_network.itemText(idx) for idx in range(self._combo_box_network.count())]
        network_idx = combo_values.index(network)
        self._combo_box_network.setCurrentIndex(network_idx)

    @property
    def scanner(self) -> str:
        return self._combo_box_scanner.currentText()

    @scanner.setter
    def scanner(self, scanner: str):
        combo_values = [self._combo_box_scanner.itemText(idx) for idx in range(self._combo_box_scanner.count())]
        scanner_idx = combo_values.index(scanner)
        self._combo_box_scanner.setCurrentIndex(scanner_idx)

    @property
    def dns_expiring_in(self) -> int:
        return self._slider_dns.value()

    @dns_expiring_in.setter
    def dns_expiring_in(self, months: int):
        self._slider_dns.setValue(months)

    @property
    def _label_path_validation_error(self) -> QLabel:
        return self._ui.labelPathValidationError

    @property
    def _combo_box_network(self) -> QComboBox:
        return self._ui.comboBoxNetwork

    @property
    def _slider_dns(self) -> QSlider:
        return self._ui.sliderDnsExpiring

    @property
    def _line_edit_user_directory(self) -> QLineEdit:
        return self._ui.lineEditUserDirectory

    @property
    def _line_edit_api_key(self) -> QLineEdit:
        return self._ui.lineEditApiKey

    @property
    def _line_edit_testnet_api_key(self) -> QLineEdit:
        return self._ui.lineEditTestnetApiKey

    @property
    def _line_edit_dns_refresh_amount(self) -> QLineEdit:
        return self._ui.lineEditDnsRefreshAmount

    @property
    def _line_edit_jetton_gas_amount(self) -> QLineEdit:
        return self._ui.lineEditJettonGasAmount

    @property
    def _combo_box_version(self) -> QComboBox:
        return self._ui.comboBoxDefaultVersion

    @property
    def _combo_box_scanner(self) -> QComboBox:
        return self._ui.comboBoxScanner

    @property
    def _button_browse(self) -> QPushButton:
        return self._ui.pushButtonBrowse

    @property
    def _button_restore_defaults(self) -> QPushButton:
        return self._ui.pushButtonRestoreDefaults

    def _on_slider_changed(self):
        months = self.dns_expiring_in
        date_to_display = dns_expire_soon_threshold(months)
        date_to_display = date_to_display.strftime("%B %Y")
        months_word = 'months' if months != 1 else 'month'
        self._dns_expiring_in_verbose = f'expiring sooner than {months} {months_word} '
        until = '(all)' if months == 12 else f'until {date_to_display}'
        self._dns_expiring_in_verbose += html_text_colored(until, _until_color())

    def _on_browse(self):
        directory = QFileDialog.getExistingDirectory(parent=self,
                                                     caption='Select user directory',
                                                     directory=self.user_directory)
        if directory != '':
            directory = Path(directory)
            self.user_directory = str(directory)

    def _on_dns_refresh_amount_edited(self):
        set_text_display_valid(self._line_edit_dns_refresh_amount, True)

    def _on_jetton_amount_edited(self):
        set_text_display_valid(self._line_edit_jetton_gas_amount, True)

    def notify_viewmodel_different(self):
        self._save_button.setDisabled(False)

    def notify_viewmodel_unchanged(self):
        self._save_button.setDisabled(True)

    def notify_user_directory_invalid(self):
        self._label_path_validation_error.setVisible(True)
        set_text_display_valid(self._line_edit_user_directory, False)

    def notify_dns_refresh_amount_invalid(self):
        set_text_display_valid(self._line_edit_dns_refresh_amount, False)

    def notify_jetton_amount_invalid(self):
        set_text_display_valid(self._line_edit_jetton_gas_amount, False)

    def focus_on_api_key(self):
        self._line_edit_api_key.setFocus()
