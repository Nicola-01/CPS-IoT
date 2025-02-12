import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import os

class IoTDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.key = ECC.generate(curve='secp256r1')
        self.public_key = self.key.public_key()

    def generate_nonce(self):
        return os.urandom(16)

    def sign_data(self, data):
        h_data = SHA256.new(data)
        signer = DSS.new(self.key, 'fips-186-3')
        return signer.sign(h_data)

    def verify_signature(self, public_key, data, signature):
        h_data = SHA256.new(data)
        verifier = DSS.new(public_key, 'fips-186-3')
        try:
            verifier.verify(h_data, signature)
            return True
        except ValueError:
            return False

    def connect(self, server):
        try:
            startTime = time.time()
            # Step 1: Generate a nonce for the device
            device_nonce = self.generate_nonce()

            # Step 2: Request authentication from the server
            server_nonce = server.generate_nonce()
            server_pubkey = server.get_public_key()

            # Step 3: Sign the server's nonce
            device_signature = self.sign_data(server_nonce)

            # Step 4: Send the device's public key, signature, and nonce to the server
            server.add_auth_request(self.device_id, server_nonce, device_nonce, self.public_key)
            server_signature = server.authenticate_device(self.device_id, self.public_key, device_signature, device_nonce)
            if server_signature is None:
                print(f"Device {self.device_id} failed device authentication.")
                return

            # Step 5: Verify the server's signature on the device's nonce
            if not self.verify_signature(server_pubkey, device_nonce, server_signature):
                print(f"Device {self.device_id} failed server authentication.")
                return

            print(f"Device {self.device_id} and server authenticated mutually.")
            print(f"Time taken for Device {self.device_id}: {time.time() - startTime} seconds")
            return time.time() - startTime
        
        except Exception as e:
            print(f"Device {self.device_id} error: {str(e)}")