import time
from Crypto.PublicKey import ECC
from crypto_utils import *


class IoTDevice:
    def __init__(self, device_id):
        self.__device_id = device_id
        self.__key = ECC.generate(curve='secp256r1') # Most Commonly Curve
        self.__public_key = self.__key.public_key()

    
    def connect(self, server):
        try:
            startTime = time.time()
            # Step 1: Generate a nonce for the device
            device_nonce = generate_nonce()

            # Step 2: Request authentication from the server
            server_nonce = server.add_auth_request(self.__device_id, device_nonce, self.__public_key)
            server_pubkey = server.get_public_key()

            # Step 3: Sign the server's nonce
            device_signature = sign_data(self.__key, server_nonce)

            # Step 4: Send the device's public key, signature, and nonce to the server
            server_signature = server.authenticate_device(self.__device_id, device_signature)
            if server_signature is None:
                print(f"Device {self.__device_id} failed device authentication.")
                return

            # Step 5: Verify the server's signature on the device's nonce
            if not verify_signature(server_pubkey, device_nonce, server_signature):
                print(f"Device {self.__device_id} failed server authentication.")
                return

            print(f"Device {self.__device_id} and server authenticated mutually.")
            print(f"Time taken for Device {self.__device_id}: {time.time() - startTime} seconds")
            return time.time() - startTime
        
        except Exception as e:
            print(f"Device {self.__device_id} error: {str(e)}")