import enum
import typing as t
from enum import Enum

import nacl.exceptions
from nacl.bindings import crypto_sign_seed_keypair

from tons.tonsdk.contract.wallet import Wallets, WalletContract
from tons.tonsdk.crypto import mnemonic_is_valid, mnemonic_to_wallet_key


class WalletSecretKind(Enum):
    mnemonics = enum.auto()
    private_key = enum.auto()


class UnknownSecretKind(ValueError):
    def __init__(self):
        super().__init__("Unknown secret kind (neither mnemonics nor private key)")


class _MnemonicReadFail(Exception):
    pass


class _PrivateKeyReadFail(Exception):
    pass


class WalletSecret:
    __slots__ = ['kind', 'mnemonics', 'public_key', 'private_key']
    kind: WalletSecretKind
    mnemonics: t.Optional[str]
    public_key: bytes
    private_key: bytes

    def __init__(self, decrypted_secret: bytes):
        try:
            self.__read_mnemonics(decrypted_secret)
        except _MnemonicReadFail:
            try:
                self.__read_pk(decrypted_secret)
            except _PrivateKeyReadFail:
                raise UnknownSecretKind

        self.__assert_consistency()

    def __eq__(self, other):
        if not isinstance(other, WalletSecret):
            return False
        return self.kind == other.kind \
            and self.mnemonics == other.mnemonics \
            and self.public_key == other.public_key \
            and self.private_key == other.private_key

    def __assert_consistency(self):
        assert bool(self.mnemonics) == (self.kind == WalletSecretKind.mnemonics)

    def __read_mnemonics(self, decrypted_secret: bytes):
        try:
            maybe_mnemonics = decrypted_secret.decode("utf-8", errors='strict')
        except UnicodeDecodeError:
            raise _MnemonicReadFail

        if not mnemonic_is_valid(maybe_mnemonics.split(' ')):
            raise _MnemonicReadFail

        self.kind = WalletSecretKind.mnemonics
        self.mnemonics = maybe_mnemonics
        self.public_key, self.private_key = mnemonic_to_wallet_key(self.mnemonics.split(' '))

    def __read_pk(self, decrypted_secret: bytes):
        self.kind = WalletSecretKind.private_key
        self.mnemonics = None
        try:
            self.public_key, self.private_key = crypto_sign_seed_keypair(decrypted_secret[:32])
        except nacl.exceptions.ValueError:
            raise _PrivateKeyReadFail

        assert self.private_key[:32] == decrypted_secret[:32], "Private key mismatch after crypto_sign_seed_keypair() function"


def get_wallet_from_record_and_secret(record, wallet_secret: WalletSecret) -> WalletContract:
    if wallet_secret.kind == WalletSecretKind.mnemonics:
        mnemonics = wallet_secret.mnemonics.split(' ')
        _, _, _, wallet = Wallets.from_mnemonics(mnemonics, record.version, record.workchain, record.subwallet_id)
    elif wallet_secret.kind == WalletSecretKind.private_key:
        pk = wallet_secret.private_key
        _, _, wallet = Wallets.from_pk(pk, record.version, record.workchain, record.subwallet_id)
    else:
        raise NotImplementedError
    return wallet
