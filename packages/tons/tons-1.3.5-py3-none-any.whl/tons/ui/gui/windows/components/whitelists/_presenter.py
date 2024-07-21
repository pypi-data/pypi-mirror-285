from tons.ui.gui.windows.components.whitelists import WhitelistsViewComponent, WhitelistsModelComponent


class WhitelistsPresenterComponent:
    def __init__(self, view_component: WhitelistsViewComponent, model_component: WhitelistsModelComponent):
        self._view = view_component
        self._model = model_component

    def display(self):
        locations = self._model.get_locations()
        self._view.set_locations(locations)
