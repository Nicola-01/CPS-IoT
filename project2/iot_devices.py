import random
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class IoTDevice:
    def __init__(self, id):
        self.__id = id
        self.__server = None
        self.__secureVault = None
        
        

    def getID(self):
        return self.__id

    def connect(self, server):
        sessionID = random.randint(0, 2**32)
        m1 = (self.__id, sessionID)

        self.__server = server
        self.__secureVault = self.__server.setUpConnection(self)
        self.__server.startAuthentication(m1)

    def sendMessage2(self, m2):
        c1, r1 = m2
        k1 = self.__secureVault.getKey(c1)

        # Ensure c2 is not equal to c1
        self.__c2 = SecureVault.generateChallenge()
        while self.__c2 == c1:
            self.__c2 = SecureVault.generateChallenge()

        self.__r2 = SecureVault.generateRandomNumber()
        self.__t1 = SecureVault.generateRandomNumber()  # Session key component

        # Concatenate payload components
        m3Payload = r1 + self.__t1 + bytes(self.__c2) + self.__r2
        m3 = self.encrypt(k1, m3Payload)
        return m3
    
    def sendMessage4(self, m4):
        k2 = self.__secureVault.getKey(self.__c2)
        k3 = bytes(a ^ b for a, b in zip(k2, self.__t1))
        
        r2, t2 = self.__parse_m4(self.decrypt(k3, m4))
        
        if (r2 == self.__r2):
            print("Device successfully authenticated")
        else:
            print("Device authentication failed")
            
        sessionKey = bytes(a ^ b for a, b in zip(t2, self.__t1))
        print(f"Session key: {sessionKey.hex()}")
        

    def encrypt(self, key, payload) -> bytes:
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

    def decrypt(self, key, payload) -> str:
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
    
    def __parse_m4(self, msg):
        M = 16

        r2 = msg[:M]
        t2 = msg[M:M*2]

        return r2, t2
        