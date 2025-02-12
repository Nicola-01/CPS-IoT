import threading
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import os

class IoTServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.key = ECC.generate(curve='secp256r1')
        self.public_key = self.key.public_key()
        self.__auth_requests = {}  # Private dictionary to store authentication requests
        self.lock = threading.Lock()

    def generate_nonce(self):
        """Generate a random nonce for the server."""
        return os.urandom(16)

    def get_public_key(self):
        """Return the server's public key."""
        return self.public_key

    def add_auth_request(self, device_id, server_nonce, device_nonce, device_public_key):
        """
        Insert authentication data into __auth_requests for a specific device_id.
        """
        with self.lock:
            self.__auth_requests[device_id] = {
                'server_nonce': server_nonce,
                'device_nonce': device_nonce,
                'device_public_key': device_public_key
            }

    def authenticate_device(self, device_id, device_public_key, device_signature, device_nonce):
        with self.lock:
            if device_id not in self.__auth_requests:
                return None

            auth_data = self.__auth_requests.pop(device_id)
            stored_server_nonce = auth_data['server_nonce']
            stored_device_nonce = auth_data['device_nonce']
            stored_device_public_key = auth_data['device_public_key']

        # Verify the device's signature on the server's nonce
        h_server_nonce = SHA256.new(stored_server_nonce)
        verifier = DSS.new(stored_device_public_key, 'fips-186-3')
        try:
            verifier.verify(h_server_nonce, device_signature)
        except ValueError:
            return None

        # Verify the device's nonce matches
        if stored_device_nonce != device_nonce:
            return None

        # Sign the device's nonce and return the signature
        h_device_nonce = SHA256.new(stored_device_nonce)
        signer = DSS.new(self.key, 'fips-186-3')
        server_signature = signer.sign(h_device_nonce)
        return server_signature

    def run(self):
        pass  # No active processing needed in this example