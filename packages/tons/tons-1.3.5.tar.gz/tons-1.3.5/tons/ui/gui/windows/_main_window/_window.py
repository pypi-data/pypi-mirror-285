from ._model import MainWindowModel
from ._presenter import MainWindowPresenter
from ._view import MainWindowView
from .._base import Window


class MainWindow(Window):
    def __init__(self):
        super().__init__()
        self._view: MainWindowView = MainWindowView()
        self._model: MainWindowModel = MainWindowModel()
        self._presenter = MainWindowPresenter(self._model, self._view)

    def show(self):
        self._view.show()
        self._view.setFocus()
        self._presenter.handle_zero_state()
        self._presenter.setup_app()

    def close(self):
        self._view.close()
