import time
import threading
from secure_vault import SecureVault
from crypto_utils import encrypt, decrypt
from global_variables import M

class IoTDevice(threading.Thread):
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
        
        super().__init__()
        self.__id = id
        self.__server = None
        self.__secureVault = None
        self.__encryptTime = 0 # Time to encrypt the message
        self.__decryptTime = 0 # Time to decrypt the message
        self.__SVupdateTime = 0 # Time to update the secure vault
        
    def getID(self):
        """Returns the device ID."""
        return self.__id

    def connect(self, server : 'IoTServer'):
        """
        Establishes a connection with the IoT server.
        
        Args:
            server (IoTServer): The IoT server to connect to.
        """
        
        self.__server = server
        self.__secureVault = self.__server.setUpConnection(self)
        self.start()
        
    def run(self):
        """Starts the IoT device thread, initialising the authentication process."""
        
        print(f"Device {self.__id} (D{self.__id}) start connection to server")
        sessionID = SecureVault.generateRandomNumber()
        m1 = (self.__id, sessionID)
        
        print(f"   D{self.__id} sends M1 to Server: {m1}")
        self.__startTime = time.time()
        self.__server.startAuthentication(m1)

    def sendMessage2(self, m2 : tuple) -> bytes:
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
        m3, self.__encryptTime  = encrypt(k1, m3Payload)
        print(f"   D{self.__id} sends M3 to Server: {m3}")
        return m3
    
    def sendMessage4(self, m4 : bytes) -> bool:
        """
        Verifies the authentication response from the server.
        
        Args:
            m4 (bytes): Encrypted message M4 from the server.
        
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        
        k2 = self.__secureVault.getKey(self.__c2)
        k3 = bytes(a ^ b for a, b in zip(k2, self.__t1))
        
        plaintext, self.__decryptTime  = decrypt(k3, m4)
        r2, t2 = self.__parse_m4(plaintext)
        
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
        self.__SVupdateTime = self.__secureVault.update_vault(sessionKey)
        
        return True
            
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
    
    def getTimings(self):
        """Returns the timing information for the device."""
        return self.__encryptTime, self.__decryptTime, self.__SVupdateTime
        