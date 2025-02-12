import os
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def generate_nonce():
    """Generate a random nonce for the server."""
    return os.urandom(16)

def sign_data(key, data):
    h_data = SHA256.new(data)
    signer = DSS.new(key, 'fips-186-3')
    return signer.sign(h_data)

def verify_signature(public_key, data, signature):
    h_data = SHA256.new(data)
    verifier = DSS.new(public_key, 'fips-186-3')
    try:
        verifier.verify(h_data, signature)
        return True
    except ValueError:
        return False
