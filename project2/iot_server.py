import threading
from iot_devices import IoTDevice
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class IoTServer:
    def __init__(self):
        super().__init__()
        self.__lock = threading.Lock()
        self.__devices = []
        self.__pairedDevices = []
        self.__SV_database = []
        self.__pendingDevices = []
        self.__condition = threading.Condition(self.__lock)

    # def run(self):
    #     print("Server listening...")

    #     with self.__condition:
    #         while len(self.__pairedDevices) == 0:
    #             self.__condition.wait()  # Wait for a signal

    #     print("Initial message sent by device")

    #     with self.__lock:
            
    def encrypt(self, key, payload) -> bytes:
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

    def decrypt(self, key, payload) -> str:
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
    
    def startAuthentication(self, m1: tuple):
        deviceID, sessionID = m1
        self.__pendingDevices.append((deviceID, sessionID))
        
        if deviceID in self.__pairedDevices:
            print("Device already connected")
            return

        device = self.getDevice(deviceID)
        self.__pairedDevices.append(deviceID)

        index = self.getDeviceIndex(deviceID)
        c1 = SecureVault.generateChallenge()
        r1 = SecureVault.generateRandomNumber()
        m2 = (c1, r1)

        k1 = self.__SV_database[index].getKey(c1)
        m3 = self.decrypt(k1, device.sendMessage2(m2))

        print(f"Decrypted message 3: {m3}")
        
        r1_received, t1, c2, r2 = self.__parse_m3(m3)
        
        if r1_received != r1:
            print("Authentication failed")
            return
        
        k2 = self.__SV_database[index].getKey(c2)
        k3 = bytes(a ^ b for a, b in zip(k2, t1))
        
        t2 = SecureVault.generateRandomNumber()
        payload = r2 + t2
        m4 = self.encrypt(k3, payload)
        
        device.sendMessage4(m4)
             

    def __parse_m3(self, msg: bytes) -> tuple:
        M = 16

        r1 = msg[:M]  # Convert byte string to actual bytes
        t1 = msg[M:M*2]  # Convert byte string to actual bytes
        c2 = msg[M*2:len(msg)-M]  # Convert list representation to actual list
        r2 = msg[-M:]  # Convert byte string to actual bytes

        return r1, t1, c2, r2

    def setUpConnection(self, device):
        self.__devices.append(device)
        self.__SV_database.append(SecureVault())
        return self.__SV_database[-1]

    def contains(self, deviceID: int):
        return self.getDeviceIndex(deviceID) != -1

    def getDevice(self, deviceID: int):
        index = self.getDeviceIndex(deviceID)
        if index != -1:
            return self.__devices[index]
        return None

    def getDeviceIndex(self, deviceID: int):
        for i, device in enumerate(self.__devices):
            if device.getID() == deviceID:
                return i
        return -1