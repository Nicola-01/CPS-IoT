import random
import threading
from secure_vault import SecureVault
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class IoTDevice():
    def __init__(self, id, server):
        super().__init__()
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
        
    # def sendMessage2(self, message):
    #     server.sendMessage2(self, message
        
        
    def sendMessage2(self, m2):
        c1, r1 = m2
        k1 = self.__secureVault.getKey(c1)
        
        equals = True
        c2 = None
        r2 = SecureVault.generateRandomNumber()
        while equals: # c2 should not be equal to c1
            c2 = SecureVault.generateChallenge()
            if c2 == c1:
                equals = False
        
        t1 = SecureVault.generateRandomNumber() # t1 is used to generate session key t  
        
        m3Payload = r1 + b"||" + t1 + b"||" + c2 + b"||" + r2
        m3 = self.encrypt_m3(k1, m3Payload)  
        return m3
                
        # sharedKey =  r1 || t1 using k1 as key
        # concatenate response and challenge for the server and send to the server
        
        # M3 = Enc (k1, r1||t1||{C2,r2})
    
    def encrypt(key, payload):
        return AES.new(key, AES.MODE_ECB).encrypt(pad(payload, 16))
    
    def decrypt(key, payload):
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(payload), 16)
        