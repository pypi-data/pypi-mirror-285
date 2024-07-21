import base64
import typing as t
import webbrowser

from tons.config import TonScannerEnum
from tons.tonclient._client._base import TransactionInfo
from tons.tonsdk.utils import Address
from tons.ui.gui.exceptions import GuiException


class TxInfoRequiredByTonCx(GuiException):
    def __init__(self, tx_hash: t.Optional[str] = None):
        super().__init__(f'ton.cx scanner requires a fetched tx_info to construct a url ({tx_hash=})')


def get_address_url(address: t.Union[str, Address], scanner: TonScannerEnum, testnet: bool) -> str:
    """
    mainnet:
        https://tonscan.org/address/%address%
        https://tonviewer.com/%address%
        https://ton.cx/address/%address%
    testnet:
        https://testnet.tonscan.org/address/%address%
        https://testnet.tonviewer.com/%address%
        https://testnet.ton.cx/address/%address%
    """
    network = 'testnet.' if testnet else ''
    base_url = {
        TonScannerEnum.tonscan: f"https://{network}tonscan.org/address/",
        TonScannerEnum.tonviewer: f"https://{network}tonviewer.com/",
        TonScannerEnum.toncx: f"https://{network}ton.cx/address/"
    }[scanner]
    address = Address(address).to_string(is_user_friendly=True, is_url_safe=True, is_bounceable=False)

    return base_url + address


def get_tx_url(tx_hash: str, testnet: bool, scanner: TonScannerEnum, tx_info: t.Optional[TransactionInfo]) -> str:
    """
    https://tonscan.org/tx/%tx_hash%
    https://tonviewer.com/transaction/%tx_hash%
    https://ton.cx/tx/%lt%:%tx_hash%:%dst_address%
    """
    network = 'testnet.' if testnet else ''
    base_url = {
        TonScannerEnum.tonscan: f"https://{network}tonscan.org/tx/",
        TonScannerEnum.tonviewer: f"https://{network}tonviewer.com/transaction/",
        TonScannerEnum.toncx: f"https://{network}ton.cx/tx/"
    }[scanner]

    if scanner == TonScannerEnum.tonscan:
        suffix = tx_hash
    elif scanner == TonScannerEnum.tonviewer:
        suffix = tx_hash
    elif scanner == TonScannerEnum.toncx:
        if tx_info is None:
            raise TxInfoRequiredByTonCx(tx_hash)
        tx_hash_b64 = base64.b64encode(bytes.fromhex(tx_hash)).decode('utf-8')
        suffix = f"{tx_info.lt}:{tx_hash_b64}:{tx_info.in_message.dst}"
    else:
        raise NotImplementedError(f"Unknown scanner: {scanner}")

    return base_url + suffix


def show_in_scanner(address: t.Union[Address, str], testnet: bool, scanner: TonScannerEnum = TonScannerEnum.tonscan):
    url = get_address_url(address, scanner, testnet)
    webbrowser.open(url)


def show_transaction_in_scanner(tx_hash: str, testnet: bool, scanner: TonScannerEnum = TonScannerEnum.tonscan,
                                tx_info: t.Optional[TransactionInfo] = None):
    url = get_tx_url(tx_hash, testnet, scanner, tx_info)
    webbrowser.open(url)


__all__ = ['show_in_scanner', 'show_transaction_in_scanner', 'get_tx_url', 'get_address_url']

