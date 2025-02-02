import os
import hmac
import hashlib
import random

N = 100 # Number of keys
M = 16 # Size of each key (in bytes)
P = 3 # Number of keys in a challenge


class SecureVault:

    def __init__(self):
        self.__keys = [os.urandom(M) for _ in range(N)]
        
        # print(f"Initial Vault (keys):")
        # Print the initial vault keys in hexadecimal format
        # for i, key in enumerate(self.__keys):
        #     print(f"  Key {i}: {key.hex()}")
        
        
    # Retrieve a key based on a list of indices, combining them using XOR
    def getKey(self, challenge):
        # Start with the first key in the list
        key = self.__keys[challenge[0]]
        for idx in challenge[1:]:
            # XOR the current key with the next key in the list
            key = bytes(a ^ b for a, b in zip(key, self.__keys[idx]))
        print(f"  XOR result: {key.hex()}")
        return key
    
    def generateChallenge():
        return random.sample(range(N), P)
    
    def generateRandomNumber():
        return os.urandom(M)

    # todo to check
    # Update the vault by performing HMAC on the concatenation of all keys
    def update_vault(self, data):
        h = hmac.new(data, b''.join(self.__keys), hashlib.sha256).digest()
        # Partition the HMAC result into segments corresponding to key sizes
        partitions = [h[i:i+len(self.__keys[0])] for i in range(0, len(h), len(self.__keys[0]))]
        for i in range(len(self.__keys)):
            # XOR each key with the corresponding partition
            print(f"  XOR between key {self.__keys[i].hex()} and partition {partitions[i % len(partitions)].hex()}")
            self.__keys[i] = bytes(a ^ b for a, b in zip(self.__keys[i], partitions[i % len(partitions)]))
            print(f"  New Key {i}: {self.__keys[i].hex()}")
