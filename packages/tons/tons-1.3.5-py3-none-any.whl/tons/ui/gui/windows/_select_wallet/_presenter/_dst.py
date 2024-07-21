from tons.ui.gui.windows._select_wallet._model import SelectWalletModel
from tons.ui.gui.windows._select_wallet._presenter._base import SelectWalletPresenter
from tons.ui.gui.windows._select_wallet._view import SelectWalletView


class SelectWalletDestinationPresenter(SelectWalletPresenter):
    def __init__(self, model: SelectWalletModel, view: SelectWalletView):
        super().__init__(model, view)
        self._view.setWindowTitle("Select address to transfer to")

    def _set_wallet_items(self):
        wallet_items = self._model.get_all_wallets()
        self._view.set_wallet_items(wallet_items)

    def display_keystore_info(self):
        self._view.keystore_name = self._model.keystore_name
        self._view.wallet_count = f'{len(self._model.get_all_wallets())} addresses'
