from typing import List

from tons.tonclient.utils import BaseKeyStore, KeyStores


class KeystoreSelectModel:
    _keystore: BaseKeyStore
    _keystores: KeyStores

    @property
    def keystore_name(self) -> str:
        return self._keystore.short_name

    @property
    def keystores_names(self) -> List[str]:
        return self._keystores.keystore_names


__all__ = ['KeystoreSelectModel']
