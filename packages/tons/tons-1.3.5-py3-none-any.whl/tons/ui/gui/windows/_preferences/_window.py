from tons.ui._utils import SharedObject
from tons.ui.gui.windows._base import NormalWindow
from tons.ui.gui.windows._preferences._model import PreferencesModel
from tons.ui.gui.windows._preferences._presenter import PreferencesPresenter
from tons.ui.gui.windows._preferences._view import PreferencesView


class PreferencesWindow(NormalWindow):
    def __init__(self, ctx: SharedObject):
        super().__init__()
        self._model: PreferencesModel = PreferencesModel(ctx.config)
        self._view: PreferencesView = PreferencesView()
        self._presenter = PreferencesPresenter(self._model, self._view)

        self.init_normal_window()

    def connect_configuration_changed(self, slot):
        self._presenter.configuration_changed.connect(slot)
