import os
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def generateNonce():
    """
    Generate a random nonce for the server or device.
    
    Returns:
        bytes: A 16-byte random nonce.
    """
    return os.urandom(16)

def signData(key : bytes, data : bytes) -> bytes:
    """
    Sign the given data using the provided ECC key.
    
    Args:
        key (ECC.EccKey): The ECC private key.
        data (bytes): The data to sign.
    
    Returns:
        bytes: The signature of the data.
    """
    h_data = SHA256.new(data)
    signer = DSS.new(key, 'fips-186-3')
    return signer.sign(h_data)

def verifySignature(public_key : bytes, data : bytes, signature : bytes) -> bool:
    """
    Verify the signature of the given data using the provided ECC public key.
    
    Args:
        public_key (ECC.EccKey): The ECC public key.
        data (bytes): The original data.
        signature (bytes): The signature to verify.
    
    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    h_data = SHA256.new(data)
    verifier = DSS.new(public_key, 'fips-186-3')
    try:
        verifier.verify(h_data, signature)
        return True
    except ValueError:
        return False