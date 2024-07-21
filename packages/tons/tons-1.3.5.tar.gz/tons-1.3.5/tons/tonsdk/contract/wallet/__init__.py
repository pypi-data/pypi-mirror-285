from typing import List, Optional, Tuple

from nacl.bindings import crypto_sign_seed_keypair

from ._multisig_v2 import (MultiSigConfig, MultiSigWalletContractV2, MultiSigInfo,
                           MultiSigOrderData, MultiSigUpdateRequest, MultiSigTransferRequest,
                           new_multisig_order_body, get_multisig_order_address, pack_multisig_order_approve)

from ._wallet_contract import SendModeEnum, WalletContract, WalletVersionEnum, InternalMessage
from ._wallet_contract_v2 import WalletV2ContractR1, WalletV2ContractR2
from ._wallet_contract_v3 import WalletV3ContractR1, WalletV3ContractR2
from ._wallet_contract_v4 import WalletV4ContractR1, WalletV4ContractR2
from ...crypto import mnemonic_new, mnemonic_to_wallet_key, mnemonic_is_valid
from ...crypto.exceptions import InvalidMnemonicsError, InvalidPrivateKeyError


class Wallets:
    default_version = WalletVersionEnum.v3r2
    ALL = {
        WalletVersionEnum.v2r1: WalletV2ContractR1,
        WalletVersionEnum.v2r2: WalletV2ContractR2,
        WalletVersionEnum.v3r1: WalletV3ContractR1,
        WalletVersionEnum.v3r2: WalletV3ContractR2,
        WalletVersionEnum.v4r1: WalletV4ContractR1,
        WalletVersionEnum.v4r2: WalletV4ContractR2,
    }

    @classmethod
    def create(cls, version: WalletVersionEnum, workchain: int,
               subwallet_id: Optional[int] = None, password: Optional[str] = None) \
            -> Tuple[List[str], bytes, bytes, WalletContract]:
        """
        :rtype: (List[str](mnemonics), bytes(public_key), bytes(private_key), WalletContract(wallet))
        """
        mnemonics = mnemonic_new(password=password)
        pub_k, priv_k = mnemonic_to_wallet_key(mnemonics)
        wallet = cls.ALL[version](
            public_key=pub_k, private_key=priv_k, wc=workchain, subwallet_id=subwallet_id)

        return mnemonics, pub_k, priv_k, wallet

    @classmethod
    def from_mnemonics(cls, mnemonics: List[str], version: WalletVersionEnum = default_version,
                       workchain: int = 0, subwallet_id: Optional[int] = None) \
            -> Tuple[List[str], bytes, bytes, WalletContract]:
        """
        :rtype: (List[str](mnemonics), bytes(public_key), bytes(private_key), WalletContract(wallet))
        """
        if not mnemonic_is_valid(mnemonics):
            raise InvalidMnemonicsError()

        pub_k, priv_k = mnemonic_to_wallet_key(mnemonics)
        wallet = cls.ALL[version](
            public_key=pub_k, private_key=priv_k, wc=workchain, subwallet_id=subwallet_id)

        return mnemonics, pub_k, priv_k, wallet

    @classmethod
    def from_pk(cls, private_key: bytes, version: WalletVersionEnum = default_version,
                workchain: int = 0, subwallet_id: Optional[int] = None):
        try:
            pub_k, _ = crypto_sign_seed_keypair(private_key[:32])
        except Exception as exc:
            raise InvalidPrivateKeyError(exc)
        wallet = cls.ALL[version](
            public_key=pub_k, private_key=private_key, wc=workchain, subwallet_id=subwallet_id)
        return pub_k, private_key, wallet

    @classmethod
    def to_addr_pk(cls, mnemonics: List[str], version: WalletVersionEnum = default_version,
                   workchain: int = 0, subwallet_id: Optional[int] = None) -> Tuple[bytes, bytes]:
        """
        :rtype: (bytes(addr), bytes(pk))
        """
        _mnemonics, _pub_k, priv_k, wallet = cls.from_mnemonics(
            mnemonics, version, workchain, subwallet_id)

        return wallet.address.to_buffer(), priv_k[:32]


__all__ = [
    'WalletV2ContractR1',
    'WalletV2ContractR2',
    'WalletV3ContractR1',
    'WalletV3ContractR2',
    'WalletV4ContractR1',
    'WalletV4ContractR2',
    'MultiSigConfig',
    'MultiSigWalletContractV2',
    'MultiSigOrderData',
    'MultiSigInfo',
    'MultiSigTransferRequest',
    'MultiSigUpdateRequest',
    'new_multisig_order_body',
    'get_multisig_order_address',
    'pack_multisig_order_approve',
    'WalletContract',
    'InternalMessage',
    'SendModeEnum',
    'WalletVersionEnum',
    'Wallets',
]
