from ._model import DialogQRModel
from ._view import DialogQRView
from ._presenter import DialogQRPresenter
from .._base import DialogWindow


class DialogQRWindow(DialogWindow):
    def __init__(self, address: str):
        super().__init__()
        self._model = DialogQRModel(address=address)
        self._view = DialogQRView()
        self._presenter = DialogQRPresenter(self._model, self._view)
