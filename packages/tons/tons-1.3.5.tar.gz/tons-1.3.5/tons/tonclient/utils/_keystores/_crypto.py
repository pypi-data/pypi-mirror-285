import os
from base64 import b64encode, b64decode
from hashlib import pbkdf2_hmac
from typing import Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from nacl.bindings import crypto_box_seed_keypair


def generate_password_keystore_key(password: str, salt: bytes) -> Tuple[bytes, bytes]:
    """
    :rtype: (bytes(public_key), bytes(secret_key))
    """
    secret = pbkdf2_hmac("sha512", password.encode('utf-8'), salt, 400_000, 32)
    return crypto_box_seed_keypair(secret)


def generate_password_keystore(password: str):
    """
    :rtype: bytes(public_key), bytes(salt)
    """
    salt = os.urandom(32)
    pub_k, _ = generate_password_keystore_key(password, salt)

    return pub_k, salt


def generate_yubikey_keystore():
    """
    256 bits key for AES and iv

    :rtype: (bytes(key), bytes(iv))
    """
    return os.urandom(32), os.urandom(16)


class AESCipher:
    def __init__(self, key, iv):
        self.block_size = algorithms.AES256.block_size
        self.key = key
        self.iv = iv

    def encrypt(self, plain_text: str):
        """ascii only"""
        plain_text = self.__pad(plain_text)
        cipher = Cipher(algorithms.AES256(self.key), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        encrypted_text = encryptor.update(plain_text.encode('utf-8')) + encryptor.finalize()
        return b64encode(encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text: bytes):
        encrypted_text = b64decode(encrypted_text)
        cipher = Cipher(algorithms.AES256(self.key), modes.CBC(self.iv))
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_text) + decryptor.finalize()
        return self.__unpad(decrypted.decode('utf-8'))

    def __pad(self, plain_text):
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text):
        last_character = plain_text[len(plain_text) - 1:]
        return plain_text[:-ord(last_character)]
