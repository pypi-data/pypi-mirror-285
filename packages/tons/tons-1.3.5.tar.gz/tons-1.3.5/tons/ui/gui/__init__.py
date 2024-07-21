import sys

if "--generate" in sys.argv:
    from tons.utils.packaging.gui import convert_qt_ui

    convert_qt_ui()



if __name__ == "__main__":
    from tons.ui.gui._main import main
    main()

__all__ = ['main']
