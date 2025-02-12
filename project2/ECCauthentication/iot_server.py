import threading
from Crypto.PublicKey import ECC
from crypto_utils import *

class IoTServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.key = ECC.generate(curve='secp256r1') # Most Commonly Curve
        self.public_key = self.key.public_key()
        self.__auth_requests = []  # Private dictionary to store authentication requests
        self.lock = threading.Lock()


    def get_public_key(self):
        """Return the server's public key."""
        return self.public_key

    def add_auth_request(self, device_id, device_nonce, device_public_key):
        """
        Insert authentication data into __auth_requests for a specific device_id.
        """
        with self.lock:
            server_nonce = generate_nonce()
            self.__auth_requests.append({
                'device_id': device_id,
                'server_nonce': server_nonce,
                'device_nonce': device_nonce,
                'device_public_key': device_public_key
            })
            return server_nonce

    def authenticate_device(self, device_id, device_signature):
        with self.lock:
            found = False
            for auth_data in self.__auth_requests:
                if auth_data['device_id'] == device_id:
                    found = True
                    break
            if not found:
                return None

            auth_data = self.__auth_requests.pop(0)
            server_nonce = auth_data['server_nonce']
            device_nonce = auth_data['device_nonce']
            device_public_key = auth_data['device_public_key']

        # Verify the device's signature on the server's nonce      
        if not verify_signature(device_public_key, server_nonce, device_signature):
            return None

        # Sign the device's nonce and return the signature
        return sign_data(self.key, device_nonce)

    def run(self):
        pass  # No active processing needed in this example