from functools import lru_cache
from typing import Dict, Sequence

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget, QFrame

from . import ui_patch
from ._qt_assets import main_window
from ..utils import theme_is_dark, invert_color


@lru_cache
def _title_color() -> QColor:
    col = QColor(235, 235, 245, int(0.6 * 0xff))
    if not theme_is_dark():
        return invert_color(col)
    return col


@ui_patch
class MainWindowUI(main_window.Ui_MainWindow):
    def post_setup_ui(self, form: QWidget):
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.WindowText, _title_color())
        for w in [self.tonsVersionLabel, self.labelKeystoreName, self.tonsVersionUpdateLabel]:
            w.setPalette(pal)

        self.tonsVersionUpdateLabel.setText(f'<a href="https://tonfactory.github.io/tons-docs/installation#update">'
                                            f'<span style=" text-decoration: underline; color:{_title_color().name(QColor.NameFormat.HexArgb)};">'
                                            f'(Update)'
                                            f'</span>'
                                            f'</a>')
        self.tonsVersionUpdateLabel.setVisible(False)

    @property
    def window_icon_name(self) -> str:
        return 'tons-interactive.ico'

    @property
    def icons_map(self) -> Dict[QWidget, str]:
        matrix = dict()
        matrix[self.pushButtonNewWallet] = 'file-circle-plus-solid.svg'
        matrix[self.pushButtonExitSearch] = 'circle-xmark-solid.svg'

        matrix[self.pushButtonRefreshAll] = 'arrows-rotate-solid.svg'

        matrix[self.pushButtonSearch] = 'magnifying-glass-solid.svg'

        matrix[self.labelTonIcon] = 'ton_symbol.svg'
        matrix[self.pushButtonFetchKeystoresBalance] = 'arrows-rotate-solid.svg'
        matrix[self.pushButtonEye] = 'eye-solid.svg'

        matrix[self.pushButtonTransactionHistory] = 'list-check-solid.svg'

        return matrix

    @property
    def lines(self) -> Sequence[QFrame]:
        return self.line, self.verticalLine
