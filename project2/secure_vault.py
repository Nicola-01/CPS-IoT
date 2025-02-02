import os
import hmac
import hashlib
import random
from global_variables import N, M, P

class SecureVault:

    def __init__(self):
        self.__keys = [os.urandom(M) for _ in range(N)]      
        
    def getKey(self, challenge):
        key = self.__keys[challenge[0]]
        for idx in challenge[1:]:
            key = bytes(a ^ b for a, b in zip(key, self.__keys[idx]))
        return key
    
    def generateChallenge():
        return random.sample(range(N), P)
    
    def generateRandomNumber():
        return os.urandom(M)

    # todo to check
    # Update the vault by performing HMAC on the concatenation of all keys
    def update_vault(self, data):
        print("Updating key ...")
        h = hmac.new(data, b''.join(self.__keys), hashlib.sha256).digest()
        # Partition the HMAC result into segments corresponding to key sizes
        
        # 0 padding at the end 
        if len(h) % M != 0:
            h = h + b'\0' * (M - len(h) % M)
            
        partitions = [h[i:i+M] for i in range(0, len(h), M)]
        for i in range(len(self.__keys)):
            self.__keys[i] = bytes(a ^ b for a, b in zip(self.__keys[i], partitions[i % len(partitions)]))
