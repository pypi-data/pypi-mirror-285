from tons.tonclient.utils import KeyStoreTypeEnum, KeyStoreAlreadyExistsError, KeyStores
from tons.tonclient.utils._keystores import KeystoreBackup
from tons.ui.gui.windows._create_keystore._model import CreateKeystoreModel


class ImportKeystoreModel(CreateKeystoreModel):  # TODO refactor SOLID
    # def __init__(self, keystores: KeyStores, backup_file_path: str):
    def __init__(self, keystores: KeyStores, keystore_backup: KeystoreBackup):
        super().__init__(keystores)
        # self._backup_file_path = backup_file_path
        self._keystore_backup: KeystoreBackup = keystore_backup

    def import_keystore(self, name: str, secret: str,
                        keystore_type: KeyStoreTypeEnum = KeyStoreTypeEnum.password):
        if keystore_type != KeyStoreTypeEnum.password:
            raise NotImplementedError("Only password keystore is supported")
        try:
            self._keystores.restore_unencrypted_keystore(name, keystore_type, secret, self._keystore_backup)
            # self._keystores.restore_tons_keystore(
            #     name, self._backup_file_path, keystore_type, secret, False)
        except KeyStoreAlreadyExistsError:
            raise

    # def import_encrypted_password_keystore_from_path(self, password: str, new_name: str):
    #     ...