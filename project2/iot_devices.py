import random
import time
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from global_variables import M

class IoTDevice:
    """
    IoT Device class that handles authentication and secure communication 
    with an IoT server using the Secure Vault mechanism.
    """
    def __init__(self, id):
        """
        Initializes an IoT device.
        
        Args:
            id (int): Unique device ID.
        """
        self.__id = id
        self.__server = None
        self.__secureVault = None
        
    def getID(self):
        """Returns the device ID."""
        return self.__id

    def connect(self, server):
        """
        Establishes a connection with the IoT server and starts authentication.
        
        Args:
            server (IoTServer): The IoT server to connect to.
        """
        
        print(f"Device {self.__id} (D{self.__id}) start connection to server")
        
        sessionID = SecureVault.generateRandomNumber()
        m1 = (self.__id, sessionID)

        self.__server = server
        self.__secureVault = self.__server.setUpConnection(self)
        
        print(f"   D{self.__id} sends M1 to Server: {m1}")
        self.__startTime = time.time()
        self.__server.startAuthentication(m1)

    def sendMessage2(self, m2):
        """
        Processes the challenge from the server and generates M3.
        
        Args:
            m2 (tuple): Challenge (C1) and random number (r1) from the server.
        
        Returns:
            bytes: Encrypted message M3.
        """
        
        c1, r1 = m2
        k1 = self.__secureVault.getKey(c1) # Derive K1 from vault keys

        # Ensure c2 is not equal to c1
        self.__c2 = SecureVault.generateChallenge()
        while self.__c2 == c1:
            self.__c2 = SecureVault.generateChallenge()

        self.__r2 = SecureVault.generateRandomNumber()
        self.__t1 = SecureVault.generateRandomNumber()

        # Concatenate payload components
        m3Payload = r1 + self.__t1 + bytes(self.__c2) + self.__r2
        m3 = self.encrypt(k1, m3Payload)
        print(f"   D{self.__id} sends M3 to Server: {m3}")
        return m3
    
    def sendMessage4(self, m4):
        """
        Verifies the authentication response from the server.
        
        Args:
            m4 (bytes): Encrypted message M4 from the server.
        
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        
        k2 = self.__secureVault.getKey(self.__c2)
        k3 = bytes(a ^ b for a, b in zip(k2, self.__t1))
        
        r2, t2 = self.__parse_m4(self.decrypt(k3, m4))
        
        if (r2 != self.__r2):
            print(f"D{self.__id}: Server authentication failed")
            return False 
        
        self.__finishTime = time.time()
        
        print(f"   D{self.__id}: Server successfully authenticated")
                    
        # Compute final session key
        sessionKey = bytes(a ^ b for a, b in zip(t2, self.__t1))
        print(f"   Session key (Device {self.__id}) for server: {sessionKey.hex()}")
        
        print(f"Device {self.__id}: time taken for authentication: {self.__finishTime - self.__startTime:.4f} seconds")
        
        # Update vault using session key
        print(f"   D{self.__id}: Update vault with session key")
        self.__secureVault.update_vault(sessionKey)
        
        return True
        

    def encrypt(self, key, payload) -> bytes:
        """
        Encrypts data using AES in CBC mode.

        Args:
            key (bytes): AES encryption key.
            payload (bytes): Data to encrypt.
        
        Returns:
            bytes: Encrypted data.
        """
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

    def decrypt(self, key, payload) -> str:
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
    
    def __parse_m4(self, msg):
        """
        Extracts r2 and t2 from M4 message.

        Args:
            msg (bytes): Decrypted M4 message.
        
        Returns:
            tuple: (r2, t2) extracted from the message.
        """
        
        r2 = msg[:M]
        t2 = msg[M:M*2]
        return r2, t2
        