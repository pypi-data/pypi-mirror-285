import logging
import sys

from PyQt6 import QtWidgets

from .utils import setup_fonts, show_system_notification, setup_palette
from .windows import MainWindow
from ...logging_ import setup_logging, tons_logger
from ...tonsdk.utils import setup_default_decimal_context


def excepthook(exc_type, exc_value, exc_tb):
    msg = f"Unexpected error occured"
    tons_logger().error(msg, exc_info=exc_value)
    QtWidgets.QApplication.exit(1)


def main():
    sys.excepthook = excepthook

    debug_mode = '--debug' in sys.argv
    setup_logging('qt', level=logging.DEBUG if debug_mode else None)
    setup_default_decimal_context()

    app = QtWidgets.QApplication(sys.argv)
    setup_palette(app)

    setup_fonts()

    main_window = MainWindow()
    show_system_notification("Welcome to Tons!", "Application Tons is ready.")
    screen = app.primaryScreen()
    main_window.move_to_center(screen)
    main_window.show()
    sys.exit(app.exec())
