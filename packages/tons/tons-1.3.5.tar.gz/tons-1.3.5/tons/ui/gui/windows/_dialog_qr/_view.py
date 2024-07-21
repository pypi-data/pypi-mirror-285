from PIL.Image import Image
from PyQt6 import QtWidgets

from tons.ui.gui.uis import DialogQRUI
from tons.ui.gui.utils import pil_to_pixmap
from tons.ui.gui.windows._base import DialogView


class DialogQRView(DialogView):
    def __init__(self):
        super().__init__(DialogQRUI)
        self._setup_signals()

    def _setup_signals(self):
        self._button_box.rejected.connect(self.close)

    def set_image(self, image: Image):
        pixmap = pil_to_pixmap(image)
        label = self._qr_label
        label.setPixmap(pixmap)

    @property
    def _qr_label(self) -> QtWidgets.QLabel:
        return self._ui.labelQR

    @property
    def _button_box(self) -> QtWidgets.QDialogButtonBox:
        return self._ui.buttonBox
