import threading
from Crypto.PublicKey import ECC
from crypto_utils import *

class IoTServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.key = ECC.generate(curve='secp256r1') # Most Commonly Curve
        self.public_key = self.key.public_key()
        self.__authRequests = []  # Private dictionary to store authentication requests
        self.lock = threading.Lock()


    def getPublicKey(self):
        """Return the server's public key."""
        return self.public_key

    def setUpConnection(self, deviceID, deviceNonce, devicePublicKey):
        """
        Insert authentication data into __auth_requests for a specific deviceID.
        """
        with self.lock:
            serverNonce = generateNonce()
            self.__authRequests.append({
                'deviceID': deviceID,
                'serverNonce': serverNonce,
                'deviceNonce': deviceNonce,
                'devicePublicKey': devicePublicKey
            })
            return serverNonce

    def startAuthentication(self, deviceID, device_signature):
        with self.lock:
            found = False
            for authData in self.__authRequests:
                if authData['deviceID'] == deviceID:
                    found = True
                    break
            if not found:
                return None

            authData = self.__authRequests.pop(0)
            serverNonce = authData['serverNonce']
            deviceNonce = authData['deviceNonce']
            devicePublicKey = authData['devicePublicKey']

        # Verify the device's signature on the server's nonce      
        if not verifySignature(devicePublicKey, serverNonce, device_signature):
            return None

        # Sign the device's nonce and return the signature
        return signData(self.key, deviceNonce)

    def run(self):
        pass  # No active processing needed in this example