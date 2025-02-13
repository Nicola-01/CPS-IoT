import time
from Crypto.PublicKey import ECC
from crypto_utils import *

class IoTDevice:
    """
    IoT Device class that handles authentication with the IoT server.
    Uses ECC for secure communication and mutual authentication.
    """
    def __init__(self, deviceID : int):
        """
        Initializes the IoT device.
        
        Args:
            deviceID (int): The unique ID of the device.
        """
        self.__deviceID = deviceID
        self.__key = ECC.generate(curve='secp256r1')  # Generate ECC key using the secp256r1 curve
        self.__public_key = self.__key.public_key()  # Extract the public key

    def connect(self, server : 'IoTServer') -> float:
        """
        Connects the device to the server and performs mutual authentication.
        
        Args:
            server (IoTServer): The IoT server to connect to.
        
        Returns:
            float: The time taken for authentication, or None if authentication fails.
        """
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