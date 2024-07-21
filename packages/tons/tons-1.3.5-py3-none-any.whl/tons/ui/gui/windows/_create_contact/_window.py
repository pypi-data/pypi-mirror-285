from typing import Optional

from tons.ui._utils import SharedObject
from ._model import CreateContactModel
from ._presenter import CreateContactPresenter
from .._base import NormalWindow
from ._view import CreateContactView
from ...utils import ContactLocation


class CreateContactWindow(NormalWindow):
    def __init__(self, ctx: SharedObject, location: Optional[ContactLocation] = None):
        super().__init__()
        self._view: CreateContactView = CreateContactView()
        self._model: CreateContactModel = CreateContactModel(ctx)
        self._presenter = CreateContactPresenter(self._model, self._view)

        self._set_pre_selected_location(location)
        self.init_normal_window()

    def connect_created(self, slot):
        self._presenter.created.connect(slot)

    def on_top(self):
        self._view.on_top()

    def _set_pre_selected_location(self, location: Optional[ContactLocation]):
        if location is not None:
            self._view.whitelists.set_location(location)
            self._presenter.set_default_contact_name()
