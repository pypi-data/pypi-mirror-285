from datetime import datetime
from functools import cached_property
from typing import Union

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QLabel

from tons.ui.gui.utils import blend_alpha, theme_is_dark, blended_hint_color


class LastActivityView:
    _label_last_activity_value_date: QLabel
    _label_last_activity_value_time: QLabel

    @property
    def last_activity(self) -> str:
        return self._label_last_activity_value_date.text() + ' ' + self._label_last_activity_value_time.text()

    @last_activity.setter
    def last_activity(self, last_activity: Union[datetime, str]):
        if isinstance(last_activity, str):
            try:
                last_activity = datetime.strptime(last_activity, "%Y %B %d %H:%M:%S")
            except ValueError:
                self._label_last_activity_value_date.setText(last_activity)
                self._label_last_activity_value_time.setText('')
                return

        date = last_activity.strftime("%Y %B %d")
        time = last_activity.strftime(f'%H:%M<font color={self._last_activity_seconds_html_color}>:%S</font>')
        self._label_last_activity_value_date.setText(date)
        self._label_last_activity_value_time.setText(time)

    @cached_property
    def _last_activity_seconds_html_color(self) -> str:
        palette = self._label_last_activity_value_time.palette()
        return blended_hint_color(palette).name()