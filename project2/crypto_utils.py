from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from global_variables import M

def encrypt(key : bytes, payload : bytes) -> bytes:
    """
    Encrypts a payload using AES-CBC mode.

    Args:
        key (bytes): AES encryption key.
        payload (bytes): Data to encrypt.

    Returns:
        bytes: Encrypted ciphertext.
    """
    return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

def decrypt(key : bytes, payload : bytes) -> str:
    """
    Decrypts AES-CBC encrypted data.

    Args:
        key (bytes): AES decryption key.
        payload (bytes): Encrypted message (Ciphertext).

    Returns:
        bytes: Decrypted plaintext.
    """
    return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)