from base64 import urlsafe_b64encode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def add_to_16_key(secret: str) -> bytes:
    return f"{secret}_robert@20220119"[0:16].encode('utf-8')


def aes_encrypt(content: bytes, secret: str = '') -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(add_to_16_key(secret), AES.MODE_CFB, iv)
    return iv + cipher.encrypt(content)


def aes_decrypt(content: bytes, secret: str = '') -> bytes:
    iv = content[:16]
    cipher = AES.new(add_to_16_key(secret), AES.MODE_CFB, iv)
    return cipher.decrypt(content[16:])


class FernetEncrypt:

    def __init__(self, user: str, psw: str):
        self.key = FernetEncrypt.generate_key(user, psw)
        self.cipher_suite = Fernet(self.key)

    @staticmethod
    def generate_key(user: str, psw: str) -> bytes:
        return urlsafe_b64encode(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=user.encode(), iterations=100000, backend=default_backend()).derive(psw.encode()))

    def decrypt(self, data: bytes) -> bytes:
        return self.cipher_suite.decrypt(data)

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher_suite.encrypt(data)
