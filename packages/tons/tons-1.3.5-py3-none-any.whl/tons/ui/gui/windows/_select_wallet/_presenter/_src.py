from tons.ui.gui.windows._select_wallet._model import SelectWalletModel
from tons.ui.gui.windows._select_wallet._presenter._base import SelectWalletPresenter
from tons.ui.gui.windows._select_wallet._view import SelectWalletView
from tons.ui.gui.windows.components.contact_kind_filter import ContactKindFilter


class SelectWalletSourcePresenter(SelectWalletPresenter):
    def __init__(self, model: SelectWalletModel, view: SelectWalletView):
        super().__init__(model, view)
        self._view.hide_new_contact_btn()
        self._view.setWindowTitle("Select wallet to transfer from")
        self._view.hide_unnecessary_buttons(necessary_kind=ContactKindFilter.keystore_wallets)

    def _set_wallet_items(self):
        wallet_items = self._model.get_wallets_records()
        self._view.set_wallet_items(wallet_items)
