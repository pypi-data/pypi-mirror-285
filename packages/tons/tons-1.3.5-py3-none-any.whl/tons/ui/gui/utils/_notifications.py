import platform
from typing import Optional

from notifypy import Notify
from pydantic import BaseModel

from tons.settings import TONS_IS_BUNDLE
from tons.ui.gui._settings import TONS_GUI_NOTIFICATION_ICO


def show_system_notification(title: str, message: str, timeout: int = 3):
    if TONS_IS_BUNDLE and platform.system() == "Darwin":
        import Foundation
        import objc

        NSUserNotification = objc.lookUpClass('NSUserNotification')
        NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')

        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)

    else:
        notification = Notify()
        notification.title = title
        notification.message = message
        notification.application_name = "Tons"
        notification.icon = TONS_GUI_NOTIFICATION_ICO
        notification.send()


class SystemNotification(BaseModel):
    title: str
    message: str
    good: Optional[bool] = None
    reset: bool = False

    def show(self):
        show_system_notification(self.title, self.message)
