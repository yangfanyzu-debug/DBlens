import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


def _get_key() -> bytes:
    key = settings.DBLENS_SECRET_KEY.encode()
    # Pad or truncate to 32 bytes for AES-256
    return key[:32].ljust(32, b'\0')


def encrypt(plaintext: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(token: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    data = base64.b64decode(token)
    nonce, ct = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ct, None).decode()
