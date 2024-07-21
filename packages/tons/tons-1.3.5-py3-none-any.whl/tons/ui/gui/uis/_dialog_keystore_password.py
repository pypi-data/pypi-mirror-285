from typing import Dict

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QProxyStyle, QStyle

from ._base import ui_patch
from ._qt_assets import dialog_keystore_password
from ..utils import macos, windows, qt_exc_handler


class EyeButtonStyle(QProxyStyle):
    @qt_exc_handler
    def drawControl(self, element, option, painter, widget = ...):
        if element == QStyle.ControlElement.CE_PushButtonBevel:
            return
        return super().drawControl(element, option, painter, widget)



@ui_patch
class DialogKeystorePasswordUI(dialog_keystore_password.Ui_Dialog):
    @property
    def icons_map(self) -> Dict[QtWidgets.QWidget, str]:
        return {self.pushButtonEye: "eye-slash-solid.svg",
                self.labelIconKeystore: "lock-solid.svg"}

    def post_setup_ui(self, form: QWidget):
        if not (macos() or windows()):
            self.pushButtonEye.setStyleSheet('')
            self.pushButtonEye.setStyle(EyeButtonStyle())
            self.pushButtonEye.setFlat(True)

