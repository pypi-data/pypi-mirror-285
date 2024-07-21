from tons.tonclient.utils import BaseKeyStore, Record, KeyStoreInvalidPasswordError, KeyStoreTypeEnum, KeyStores


class DialogKeystorePasswordModel:
    def __init__(self, keystore: BaseKeyStore):
        if keystore.type == KeyStoreTypeEnum.yubikey:
            raise NotImplementedError("Yubikey is not supported in GUI yet")
        self._keystore = keystore

    def enter_sensitive(self, secret: str):
        try:
            self._keystore.validate_secret(secret)
        except KeyStoreInvalidPasswordError:
            raise
        else:
            KeyStores.enter_sensitive(self._keystore, password=secret)
