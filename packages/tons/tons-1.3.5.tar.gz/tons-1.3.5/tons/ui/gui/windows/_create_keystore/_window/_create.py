from tons.ui._utils import SharedObject
from ..._base import NormalWindow
from .._model import CreateKeystoreModel
from .._view import CreateKeystoreView, ImportKeystoreView
from .._presenter import CreateKeystorePresenter


class CreateKeystoreWindow(NormalWindow):
    def __init__(self, ctx: SharedObject):
        super().__init__()
        self._model = CreateKeystoreModel(ctx.keystores)  # todo pass ctx instead of keystores
        self._view: CreateKeystoreView = CreateKeystoreView()
        self._presenter = CreateKeystorePresenter(self._model, self._view)

        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)
