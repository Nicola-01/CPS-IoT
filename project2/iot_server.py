import threading
from iot_devices import IoTDevice
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class IoTServer(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.__lock = threading.Lock()
        self.__devices = []
        self.__pairedDevices = []
        self.__SV_database = []
        self.__pendingDevices = []
        
    def run(self):
        print("Server listening...")
                
        while len(self.__pairedDevices) == 0:
            pass
        
        print(f"Initial message sent by device")
        
        with self.__lock:
            deviceID, sessionID = self.__pendingDevices.pop(0)
            
            
            if self.__pairedDevices.contains(deviceID):
                print("Device already connected")
                return
            
            device = self.getDevice(deviceID)
            
            self.__pairedDevices.append(deviceID)
            
            index = self.getDeviceIndex(deviceID)

            c1 = SecureVault.generateChallenge()
            r1 = SecureVault.generateRandomNumber()
            m2 = (c1, r1)
            
            k1 = self.__SV_database[index].getKey(c1)
                        
            m3 = self.decrypt(k1, self.getDevice(deviceID).sendMessage2(m2))
            
            print(f"Decrypted message 3: {m3}")
            
            
            
    def encrypt(key, payload):
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))
    
    def decrypt(key, cypher):
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(cypher), 16)
        
        
    def startAuthentication(self, m1: tuple):
        deviceID, sessionID = m1
        self.__pendingDevices.append((deviceID, sessionID))
        print(f"Devices {len(self.__pendingDevices)}")
                
    def setUpConnection(self, device: IoTDevice):
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

        
        

    def sendMessage3(self, device, message):
        
        challenge = message.get_challenge()
        size = len(challenge)
        
        k1 = 0b1 * 8 * SecureVault.M
        
        for i in range(size):
            k1 ^= challenge[i]