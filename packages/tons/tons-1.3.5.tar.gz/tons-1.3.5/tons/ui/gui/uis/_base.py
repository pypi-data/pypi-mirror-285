from typing import Dict, Sequence

from PyQt6.QtWidgets import QWidget, QAbstractButton, QLabel, QFrame, QGraphicsOpacityEffect

from tons.ui.gui.utils import decorates, get_icon, set_icon


class _UIBase:
    def post_setup_ui(self, form: QWidget):
        self._setup_icons(form)
        self._setup_lines_opacity()

    def _setup_lines_opacity(self):
        for line in self.lines:
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.15)
            line.setGraphicsEffect(opacity_effect)

    def _setup_icons(self, form: QWidget):
        for widget, icon_name in self.icons_map.items():
            assert isinstance(widget, QLabel) or isinstance(widget, QAbstractButton)
            set_icon(widget, icon_name)

        window_icon = get_icon(self.window_icon_name)
        form.setWindowIcon(window_icon)

    @property
    def window_icon_name(self) -> str:
        return 'blank.png'

    @property
    def icons_map(self) -> Dict[QWidget, str]:
        """ All icons should go here """
        return dict()

    @property
    def lines(self) -> Sequence[QFrame]:
        return tuple()


def ui_patch(cls):
    @decorates(cls)
    class DecoratedUI(cls, _UIBase):
        def setupUi(self, form):
            form.setUpdatesEnabled(False)

            cls.setupUi(self, form)
            _UIBase.post_setup_ui(self, form)
            super().post_setup_ui(form)

            form.setUpdatesEnabled(True)

    return DecoratedUI


__all__ = ['ui_patch']
