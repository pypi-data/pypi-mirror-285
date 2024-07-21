import hashlib
import hmac
from typing import Union

import nacl.utils
from cryptography.exceptions import UnsupportedAlgorithm, _Reasons
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fe25519 import fe25519
from ge25519 import ge25519, ge25519_p3

from tons.tonsdk.boc import Cell
from tons.tonsdk.utils import Address


def _get_salt(sender_address: Union[str, Address]) -> bytes:
    return bytes(Address(sender_address).to_string(True, True, True, False), 'utf-8')


def _get_prefix_length(message_length: int) -> int:
    return 16 + (16 - message_length % 16) % 16


def _get_random_prefix(message_length: int) -> bytes:
    prefix_length = _get_prefix_length(message_length)
    assert (prefix_length + message_length) % 16 == 0
    assert 16 <= prefix_length < 32
    return bytes((prefix_length,)) + nacl.utils.random(prefix_length - 1)


def _get_data(message: str) -> bytes:
    message_bytes = bytes(message, 'utf-8')
    return _get_random_prefix(len(message_bytes)) + message_bytes


def __hmac_sha512(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha512).digest()


def _get_msg_key(salt: bytes, data: bytes) -> bytes:
    return __hmac_sha512(salt, data)[:16]


def _get_pub_xor(public_key_1: bytes, public_key_2: bytes) -> bytes:
    return bytes(p1 ^ p2 for p1, p2 in zip(public_key_1, public_key_2))


def _encrypt_data(data: bytes, shared_key: bytes, msg_key: bytes) -> bytes:
    x = __hmac_sha512(shared_key, msg_key)
    key = x[0:32]
    iv = x[32:48]
    cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def _make_snake_cells(payload: bytes) -> Cell:
    ROOT_CELL_BYTE_LENGTH = 35 + 4
    # CELL_BYTE_LENGTH = 127

    root_cell = Cell()
    root_cell.bits.write_bytes(payload[:ROOT_CELL_BYTE_LENGTH])
    payload = payload[ROOT_CELL_BYTE_LENGTH:]

    prev_cell = root_cell
    previous_payload_length = None
    while payload:
        cur_cell = Cell()
        free_bytes = cur_cell.bits.get_free_bytes()
        cur_cell.bits.write_bytes(payload[:free_bytes])
        payload = payload[free_bytes:]
        prev_cell.store_ref(cur_cell)
        prev_cell = cur_cell
        if len(payload) == previous_payload_length:
            raise RuntimeError("unexpected infinite loop in _make_snake_cells(): payload won't shrink")
        previous_payload_length = len(payload)

    return root_cell


def _x25519_from_ed25519_private_bytes(private_bytes):
    if not backend.x25519_supported():
        raise UnsupportedAlgorithm(
            "X25519 is not supported by this version of OpenSSL.",
            _Reasons.UNSUPPORTED_EXCHANGE_ALGORITHM,
        )

    hasher = hashes.Hash(hashes.SHA512())
    hasher.update(private_bytes)
    h = bytearray(hasher.finalize())

    # curve25519 clamping
    h[0] &= 248
    h[31] &= 127
    h[31] |= 64

    return bytes(h[0:32])


def _x25519_from_ed25519_public_bytes(public_bytes):
    if not backend.x25519_supported():
        raise UnsupportedAlgorithm(
            "X25519 is not supported by this version of OpenSSL.",
            _Reasons.UNSUPPORTED_EXCHANGE_ALGORITHM,
        )

    # This is libsodium's crypto_sign_ed25519_pk_to_curve25519 translated into
    # the Python module ge25519.
    if ge25519.has_small_order(public_bytes) != 0:
        raise ValueError("Doesn't have small order")

    # frombytes in libsodium appears to be the same as
    # frombytes_negate_vartime; as ge25519 only implements the from_bytes
    # version, we have to do the root check manually.
    A = ge25519_p3.from_bytes(public_bytes)
    if A.root_check:
        raise ValueError("Root check failed")

    if not A.is_on_main_subgroup():
        raise ValueError("It's on the main subgroup")

    one_minus_y = fe25519.one() - A.Y
    x = A.Y + fe25519.one()
    x = x * one_minus_y.invert()

    return bytes(x.to_bytes())


def encrypt_message(message: str, my_public_key: Union[bytes, bytearray], their_public_key: Union[bytes, bytearray],
                    my_private_key: Union[bytes, bytearray], sender_address: Union[str, Address]):
    message = str(message)
    if len(message) > 960:
        raise OverflowError(f"Message too long: {len(message)=} > 960")

    my_public_key = bytes(my_public_key)
    their_public_key = bytes(their_public_key)
    my_private_key = bytes(my_private_key)[:32]
    sender_address = Address(sender_address)

    x25519_priv_k = _x25519_from_ed25519_private_bytes(my_private_key)
    x25519_pub_k = _x25519_from_ed25519_public_bytes(their_public_key)
    shared_secret = X25519PrivateKey.from_private_bytes(x25519_priv_k).exchange(
        X25519PublicKey.from_public_bytes(x25519_pub_k))

    salt = _get_salt(sender_address)
    data = _get_data(message)
    msg_key = _get_msg_key(salt, data)
    encrypted_data = _encrypt_data(data, shared_secret, msg_key)
    pub_xor = _get_pub_xor(my_public_key, their_public_key)
    op_tag = bytes.fromhex('2167da4b')
    assert len(op_tag) == 4
    assert len(pub_xor) == 32
    assert len(msg_key) == 16

    payload = op_tag + pub_xor + msg_key + encrypted_data
    return _make_snake_cells(payload)
