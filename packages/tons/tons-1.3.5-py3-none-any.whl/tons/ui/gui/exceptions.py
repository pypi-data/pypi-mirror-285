class GuiException(Exception):
    pass


class CtxReferenceError(ReferenceError, GuiException):
    pass


class KeystoreNotUnlocked(GuiException):
    def __init__(self):
        super().__init__('User cancelled the keystore unlock')
