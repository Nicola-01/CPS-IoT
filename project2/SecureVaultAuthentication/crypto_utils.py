import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from global_variables import M

def encrypt(key : bytes, payload : bytes) -> tuple:
    """
    Encrypts a payload using AES-CBC mode.

    Args:
        key (bytes): AES encryption key.
        payload (bytes): Data to encrypt.

    Returns:
        bytes: Encrypted ciphertext.
        float: Time taken to encrypt the payload.
    """
    
    startTime = time.time()
    return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16)), time.time() - startTime

def decrypt(key : bytes, payload : bytes) -> tuple:
    """
    Decrypts AES-CBC encrypted data.

    Args:
        key (bytes): AES decryption key.
        payload (bytes): Encrypted message (Ciphertext).

    Returns:
        bytes: Decrypted plaintext.
        float: Time taken to decrypt the payload.
    """
    
    startTime = time.time()
    return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16), time.time() - startTime