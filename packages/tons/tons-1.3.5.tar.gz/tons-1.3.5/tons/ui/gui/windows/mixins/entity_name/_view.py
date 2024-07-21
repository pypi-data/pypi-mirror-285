from PyQt6.QtWidgets import QLineEdit, QLabel

from tons.ui.gui.windows.components.entity_name import NameViewComponent, InvalidNameNotification


class NameView:
    def init_name_view(self, validation_label: QLabel, line_edit: QLineEdit):
        self._name_view_component = NameViewComponent(validation_label, line_edit)

    @staticmethod
    def _invalid_name_notification_text(kind: InvalidNameNotification):
        text = {
            InvalidNameNotification.empty: "Come up with a catchy name!",
            InvalidNameNotification.exists: "Another entity with this name already exists"
        }[kind]
        return text

    def notify_invalid_name(self, kind: InvalidNameNotification):
        self._name_view_component.set_name_validity(False)
        text = self._invalid_name_notification_text(kind)
        self._name_view_component.notify_name_validation_error(text)

    def hide_name_validation_error_notification(self):
        self._name_view_component.hide_name_validation_error()


__all__ = ['InvalidNameNotification',
           'NameView']