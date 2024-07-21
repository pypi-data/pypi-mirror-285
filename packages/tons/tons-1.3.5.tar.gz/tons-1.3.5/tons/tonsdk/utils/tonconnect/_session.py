from typing import Optional

import nacl.utils
from nacl.public import PublicKey, PrivateKey, Box


class Session:
    """
    Protocol: https://github.com/ton-blockchain/ton-connect/blob/main/session.md
    """
    nonce_len = 24

    def __init__(self, app_public_key: PublicKey, private_key: Optional[PrivateKey] = None):
        if private_key is None:
            private_key = PrivateKey.generate()

        self.private_key = private_key
        self.app_public_key: PublicKey = app_public_key
        self.session_id: str = bytes(self.private_key.public_key).hex()

    def encrypt_msg(self, message: str, nonce: Optional[bytes] = None) -> nacl.utils.EncryptedMessage:
        if nonce is None:
            nonce = self.create_nonce()

        encoded_message = message.encode()

        box = Box(self.private_key, self.app_public_key)
        encrypted = box.encrypt(encoded_message, nonce)

        return encrypted

    def decrypt_msg(self, message: nacl.utils.EncryptedMessage) -> str:
        box = Box(self.private_key, self.app_public_key)
        decrypted = box.decrypt(message)

        return decrypted.decode()

    def create_nonce(self) -> bytes:
        return nacl.utils.random(self.nonce_len)

    @staticmethod
    def public_key_from_hex(hex_data):
        return PublicKey(bytes.fromhex(hex_data))

    @staticmethod
    def public_key_to_hex(public_key: PublicKey):
        return public_key.encode().hex()
