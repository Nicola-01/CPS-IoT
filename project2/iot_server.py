import copy
import threading
from iot_devices import IoTDevice
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from global_variables import M

class IoTServer(threading.Thread):
    """
    IoT Server that listens for device connections and manages authentication
    using a secure vault.
    """

    
    def __init__(self):
        """
        Initializes the IoT server.
        """
        
        super().__init__()
        self.__lock = threading.Lock()
        self.__condition = threading.Condition(self.__lock)  # Condition variable
        
        self.__SV_database = []
        self.__devices = [] # List of IoTDevice objects
        self.__pairedDevices = [] # List of device IDs that have been paired
        self.__pendingDevices = [] # List of device IDs that are pending

    def run(self):
        """
        Main server loop that listens for authentication requests.
        """
        
        print("Server listening...")

        while True:
            with self.__condition:
                while len(self.__pendingDevices) == 0:  # Wait until a device is pending
                    self.__condition.wait() 

                print("Initial message sent by device")
                
                # Get the first pending device
                deviceID, sessionID = self.__pendingDevices.pop(0)
                            
                device = self.getDevice(deviceID)
                index = self.getDeviceIndex(deviceID)
                secureVault = self.__SV_database[index]

                # Generate server's challenge
                c1 = SecureVault.generateChallenge()
                r1 = SecureVault.generateRandomNumber()
                m2 = (c1, r1)

                k1 = secureVault.getKey(c1)
                m3 = self.decrypt(k1, device.sendMessage2(m2))
                
                # Parse M3 message
                r1_received, t1, c2, r2 = self.__parse_m3(m3)
                
                # Verify received challenge response
                if r1_received != r1:
                    print("Authentication failed: r1 mismatch.")
                    return
                
                # Generate k2, k3, and t2
                k2 = secureVault.getKey(c2)
                k3 = bytes(a ^ b for a, b in zip(k2, t1))
                t2 = SecureVault.generateRandomNumber()
                
                # Generate M4 message
                payload = r2 + t2
                m4 = self.encrypt(k3, payload)
                
                # Authenticate device
                if(device.sendMessage4(m4)):
                    sessionKey = bytes(a ^ b for a, b in zip(t2, t1))
                    print(f"Session key Server: {sessionKey.hex()}")
                    
                    # Update secure vault
                    secureVault.update_vault(sessionKey)

                    # Add device to paired list in a thread-safe way
                    with self.__lock:
                        self.__pairedDevices.append(deviceID)
                
                else:
                    print("Authentication failed at M4 verification.")

            
    def encrypt(self, key, payload) -> bytes:
        """
        Encrypts a payload using AES-CBC mode with a random IV.

        Args:
            key (bytes): AES encryption key.
            payload (bytes): Data to encrypt.

        Returns:
            bytes: Encrypted data with IV prepended.
        """
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

    def decrypt(self, key, payload) -> str:
        """
        Decrypts AES-CBC encrypted data.

        Args:
            key (bytes): AES decryption key.
            payload (bytes): Encrypted message (IV + Ciphertext).

        Returns:
            bytes: Decrypted plaintext.
        """
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
    
    def startAuthentication(self, m1: tuple):
        """
        Adds a device to the authentication queue.

        Args:
            m1 (tuple): (deviceID, sessionID)
        """
        
        deviceID, sessionID = m1
                
        print(f"Device {deviceID} waiting for append")
        with self.__lock:
            if int(deviceID) in map(int, self.__pairedDevices):
                print("Device already connected")
                return False
        print(f"Device {deviceID} comming for append")
        
        with self.__condition:
            print(f"Device {deviceID} appended")
            self.__pendingDevices.append((deviceID, sessionID))
            self.__condition.notify()
             

    def __parse_m3(self, msg: bytes) -> tuple:
        """
        Parses M3 message received from the IoT device.

        Args:
            msg (bytes): Decrypted M3 message.

        Returns:
            tuple: Extracted values (r1, t1, c2, r2).
        """
        
        r1 = msg[:M]
        t1 = msg[M:M*2]
        c2 = msg[M*2:len(msg)-M]
        r2 = msg[-M:]

        return r1, t1, c2, r2

    def setUpConnection(self, device):
        """
        Registers a new IoT device.

        Args:
            device (IoTDevice): The IoT device to register.

        Returns:
            SecureVault: A copy of the device's secure vault.
        """
        
        with self.__lock:
            self.__devices.append(device)
            self.__SV_database.append(SecureVault())
            return copy.deepcopy(self.__SV_database[-1])

    def contains(self, deviceID: int):
        """
        Checks if a device is already registered.

        Args:
            deviceID (int): Device ID.

        Returns:
            bool: True if the device is registered, False otherwise.
        """
        return self.getDeviceIndex(deviceID) != -1

    def getDevice(self, deviceID: int):
        """
        Retrieves a registered IoT device.

        Args:
            deviceID (int): Device ID.

        Returns:
            IoTDevice: The corresponding IoT device, or None if not found.
        """
        index = self.getDeviceIndex(deviceID)
        if index != -1:
            return self.__devices[index]
        return None

    def getDeviceIndex(self, deviceID: int):
        """
        Finds the index of a device in the device list.

        Args:
            deviceID (int): Device ID.

        Returns:
            int: The index of the device, or -1 if not found.
        """
        for i, device in enumerate(self.__devices):
            if device.getID() == deviceID:
                return i
        return -1