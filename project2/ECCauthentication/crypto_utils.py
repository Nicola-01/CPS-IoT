import os
import time
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def generateNonce():
    """
    Generate a random nonce for the server or device.
    
    Returns:
        bytes: A 16-byte random nonce.
    """
    return os.urandom(16)

def signData(key : bytes, data : bytes) -> tuple:
    """
    Sign the given data using the provided ECC key.
    
    Args:
        key (ECC.EccKey): The ECC private key.
        data (bytes): The data to sign.
    
    Returns:
        bytes: The signature of the data.
        float: Time taken to sign the data.
    """
    
    startTime = time.time()
    signer = DSS.new(key, 'fips-186-3')
    return signer.sign(SHA256.new(data)), time.time() - startTime 

def verifySignature(public_key : bytes, data : bytes, signature : bytes) -> tuple:
    """
    Verify the signature of the given data using the provided ECC public key.
    
    Args:
        public_key (ECC.EccKey): The ECC public key.
        data (bytes): The original data.
        signature (bytes): The signature to verify.
    
    Returns:
        bool: True if the signature is valid, False otherwise.
        float: Time taken to decrverify the signature.
    """
    
    try:
        startTime = time.time()
        verifier = DSS.new(public_key, 'fips-186-3')
        verifier.verify(SHA256.new(data), signature)
        return True, time.time() - startTime
    except ValueError:
        return False