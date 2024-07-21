from tons.tonclient.utils import KeyStoreTypeEnum
from tons.tonclient.utils import KeyStoreNameInvalidError, KeyStoreAlreadyExistsError, \
    KeyStoreShortPasswordError
from tons.tonclient.utils._keystores import PasswordKeyStore, KeyStores
from tons.ui.gui.exceptions import GuiException


class CreateKeystoreModel:
    def __init__(self, keystores: KeyStores):
        self._keystores: KeyStores = keystores

    @staticmethod
    def validate_passwords(password1: str, password2: str):
        if password1 != password2:
            raise PasswordsDoNotMatch()
        CreateKeystoreModel.validate_password(password1)

    @staticmethod
    def validate_password(password):
        """
        Raises:
            KeyStoreInvalidPasswordError
        """
        try:
            PasswordKeyStore.validate_password(password)
        except KeyStoreShortPasswordError:
            raise

    @property
    def default_keystore_name(self):
        new_keystore_base_name = "New keystore"
        new_keystore_pattern = new_keystore_base_name + " %03d"
        new_keystore_name = "Default keystore"
        idx = 1
        while self._keystore_exists(new_keystore_name):
            new_keystore_name = new_keystore_pattern % idx
            idx += 1
        return new_keystore_name

    def create_keystore(self, name: str, secret: str, keystore_type: KeyStoreTypeEnum = KeyStoreTypeEnum.password):
        if keystore_type != KeyStoreTypeEnum.password:
            raise NotImplementedError("Only password keystore is supported")
        try:
            self._keystores.create_new_keystore(name, keystore_type, secret, save=True)
        except (KeyStoreNameInvalidError, KeyStoreAlreadyExistsError):
            raise

    def _keystore_exists(self, name: str) -> bool:
        return self._keystores.keystore_already_exists(name)


class PasswordsDoNotMatch(GuiException):
    def __init__(self):
        super().__init__('Passwords do not match')
