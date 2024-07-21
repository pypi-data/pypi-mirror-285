from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from tons.logging_ import tons_logger
from tons.ui.gui.utils import slot_exc_handler
from .._model import CreateKeystoreModel, PasswordsDoNotMatch
from .._view import CreateKeystoreView

from .._model import KeyStoreShortPasswordError, KeyStoreTypeEnum, KeyStoreNameInvalidError, KeyStoreAlreadyExistsError
from .._view import InvalidNameNotification


class CreateKeystorePresenter(QObject):
    created = pyqtSignal()

    def __init__(self, model: CreateKeystoreModel, view: CreateKeystoreView):
        super().__init__()
        self._model: CreateKeystoreModel = model
        self._view: CreateKeystoreView = view
        self._view.setup_signals(self)
        self.set_default_keystore_name()

    def set_default_keystore_name(self):
        default_keystore_name = self._model.default_keystore_name
        self._view.keystore_name = default_keystore_name

    @pyqtSlot()
    @slot_exc_handler()
    def on_create_clicked(self):
        self._view.hide_validation_errors()

        password1 = self._view.password_1
        password2 = self._view.password_2
        bad = False
        try:
            self._model.validate_passwords(password1, password2)
        except PasswordsDoNotMatch:
            self._view.notify_passwords_do_not_match(highlight=True)
            bad = True
        except KeyStoreShortPasswordError as exc:
            self._view.notify_password_too_short(exc.min_symbols, highlight=True)
            bad = True

        if not self._view.keystore_name:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
            bad = True

        if bad:
            return

        if not self._view.protection_type == 'Password':
            raise NotImplementedError('Yubikey keystore is not supported yet')

        try:
            self._create()
        except KeyStoreNameInvalidError:
            self._view.notify_invalid_name(InvalidNameNotification.empty)
        except KeyStoreAlreadyExistsError:
            self._view.notify_invalid_name(InvalidNameNotification.exists)
        except Exception as exception:
            tons_logger().error(f'{type(exception).__name__}', exc_info=exception)
            self._view.notify_unexpected_error(exception)
        else:
            self.created.emit()
            self._view.close()

    def _create(self):
        keystore_type = KeyStoreTypeEnum.password
        keystore_name = self._view.keystore_name
        assert self._view.password_1 == self._view.password_2
        secret = self._view.password_1
        self._model.create_keystore(keystore_name, secret, keystore_type)

    @pyqtSlot()
    @slot_exc_handler()
    def on_password_1_edited(self):
        pass

    @pyqtSlot()
    @slot_exc_handler()
    def on_password_2_edited(self):
        pass
