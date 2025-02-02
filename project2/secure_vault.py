import os
import hmac
import hashlib
import random

N = 100 # Number of keys
M = 10 # Size of each key (in bytes)


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
        print(f"  Initial Key from Vault: {key.hex()}")
        for idx in challenge[1:]:
            # XOR the current key with the next key in the list
            print(f"  XOR between key {key.hex()} and key {self.keys[idx].hex()}")
            key = bytes(a ^ b for a, b in zip(key, self.keys[idx]))
            print(f"  XOR result: {key.hex()}")
        return key
    
    def generateChallenge(self):
        return random.sample(range(self.N), self.P)
    
    def generateRandomNumber(self):
        return random.randint(0, 2**32)

    # todo to check
    # Update the vault by performing HMAC on the concatenation of all keys
    def update_vault(self, data):
        h = hmac.new(data, b''.join(self.keys), hashlib.sha256).digest()
        # Partition the HMAC result into segments corresponding to key sizes
        partitions = [h[i:i+len(self.keys[0])] for i in range(0, len(h), len(self.keys[0]))]
        for i in range(len(self.keys)):
            # XOR each key with the corresponding partition
            print(f"  XOR between key {self.keys[i].hex()} and partition {partitions[i % len(partitions)].hex()}")
            self.keys[i] = bytes(a ^ b for a, b in zip(self.keys[i], partitions[i % len(partitions)]))
            print(f"  New Key {i}: {self.keys[i].hex()}")
