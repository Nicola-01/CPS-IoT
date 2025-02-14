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
        startTime = time.time()
        self.__key = ECC.generate(curve='secp256r1')  # Generate ECC key using the secp256r1 curve
        self.__keyGenTime = time.time() - startTime
        self.__public_key = self.__key.public_key()  # Extract the public key

    def connect(self, server : 'IoTServer') -> tuple:
        """
        Connects the device to the server and performs mutual authentication.
        
        Args:
            server (IoTServer): The IoT server to connect to.
        
        Returns:
            tuple: A tuple containing the time taken for key generation, signing, verification, and authentication.
                   If authentication fails, the tuple contains None.
        """
        try:
            startTime = time.time()
            # Generate a nonce for the device
            deviceNonce = generateNonce()

            # Request authentication from the server
            serverNonce = server.setUpConnection(self.__deviceID, deviceNonce, self.__public_key)
            serverPubKey = server.getPublicKey()

            # Sign the server's nonce
            deviceSignature, signTime = signData(self.__key, serverNonce)

            # Send the device's public key, signature, and nonce to the server
            serverSignature = server.startAuthentication(self.__deviceID, deviceSignature)
            if serverSignature is None:
                print(f"Device {self.__deviceID} failed device authentication.")
                return

            # Verify the server's signature on the device's nonce
            verify, verifyTime = verifySignature(serverPubKey, deviceNonce, serverSignature)    
            if not verify:
                print(f"Device {self.__deviceID} failed server authentication.")
                return

            authenticationTime = time.time() - startTime

            print(f"Device {self.__deviceID} and server authenticated mutually.")
            print(f"Time taken for Device {self.__deviceID}: {authenticationTime} seconds")
            return self.__keyGenTime, signTime, verifyTime, authenticationTime
        
        except Exception as e:
            print(f"Device {self.__deviceID} error: {str(e)}")