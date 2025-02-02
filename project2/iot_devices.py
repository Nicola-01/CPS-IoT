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
        c2 = SecureVault.generateChallenge()
        while c2 == c1:
            c2 = SecureVault.generateChallenge()

        r2 = SecureVault.generateRandomNumber()
        t1 = SecureVault.generateRandomNumber()  # Session key component

        # Concatenate payload components
        m3Payload = r1 + "||" + t1 + "||" + c2 + "||" + r2
        m3 = self.encrypt(k1, m3Payload)
        return m3

    def encrypt(self, key, payload):
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))

    def decrypt(self, key, payload):
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
        