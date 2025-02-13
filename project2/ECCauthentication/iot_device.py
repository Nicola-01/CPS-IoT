import time
from Crypto.PublicKey import ECC
from crypto_utils import *


class IoTDevice:
    def __init__(self, device_id):
        self.__deviceID = device_id
        self.__key = ECC.generate(curve='secp256r1') # Most Commonly Curve
        self.__public_key = self.__key.public_key()

    
    def connect(self, server):
        try:
            startTime = time.time()
            # Step 1: Generate a nonce for the device
            deviceNonce = generateNonce()

            # Step 2: Request authentication from the server
            serverNonce = server.setUpConnection(self.__deviceID, deviceNonce, self.__public_key)
            serverPubKey = server.getPublicKey()

            # Step 3: Sign the server's nonce
            device_signature = signData(self.__key, serverNonce)

            # Step 4: Send the device's public key, signature, and nonce to the server
            server_signature = server.startAuthentication(self.__deviceID, device_signature)
            if server_signature is None:
                print(f"Device {self.__deviceID} failed device authentication.")
                return

            # Step 5: Verify the server's signature on the device's nonce
            if not verifySignature(serverPubKey, deviceNonce, server_signature):
                print(f"Device {self.__deviceID} failed server authentication.")
                return

            print(f"Device {self.__deviceID} and server authenticated mutually.")
            print(f"Time taken for Device {self.__deviceID}: {time.time() - startTime} seconds")
            return time.time() - startTime
        
        except Exception as e:
            print(f"Device {self.__deviceID} error: {str(e)}")