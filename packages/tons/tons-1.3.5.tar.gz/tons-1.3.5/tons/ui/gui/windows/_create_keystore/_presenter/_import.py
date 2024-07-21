from tons.tonclient.utils import KeyStoreTypeEnum
from ._create import CreateKeystorePresenter
from .._model import ImportKeystoreModel
from .._view import ImportKeystoreView


class ImportKeystorePresenter(CreateKeystorePresenter):  # TODO refactor SOLID
    _model: ImportKeystoreModel

    def __init__(self, model: ImportKeystoreModel, view: ImportKeystoreView):
        super().__init__(model, view)

    def _create(self):
        keystore_type = KeyStoreTypeEnum.password
        keystore_name = self._view.keystore_name
        assert self._view.password_1 == self._view.password_2
        secret = self._view.password_1
        self._model.import_keystore(keystore_name, secret, keystore_type)
