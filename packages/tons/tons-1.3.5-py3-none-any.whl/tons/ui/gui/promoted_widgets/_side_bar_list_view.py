from PyQt6.QtWidgets import QListView

from tons.ui.gui.utils import set_selection_color_for_light_theme


class SideBarListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_selection_color_for_light_theme(self)
