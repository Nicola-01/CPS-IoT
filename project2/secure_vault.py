import os
import hmac
import hashlib
import random
from global_variables import N, M, P

class SecureVault:
    """
    SecureVault manages a set of keys shared between an IoT device and an IoT server.
    The vault is used for authentication and is updated dynamically after each session.
    """

    def __init__(self):
        """
        Initializes the secure vault with N keys, each of size M bytes.
        The keys are randomly generated during initialization.
        """
        self.__keys = [os.urandom(M) for _ in range(N)]      
        
    def getKey(self, challenge : list[int]) -> bytes:
        """
        Computes the session key using XOR on a subset of keys from the vault.
        
        Args:
            challenge (list[int]): A list of P indices referring to keys in the vault.
        
        Returns:
            bytes: The computed session key of M bytes.
        """
        key = self.__keys[challenge[0]]
        for idx in challenge[1:]:
            key = bytes(a ^ b for a, b in zip(key, self.__keys[idx]))
        return key
    
    @staticmethod
    def generateChallenge() -> list[int]:
        """
        Generates a random challenge consisting of P distinct indices from the secure vault.

        Returns:
            list[int]: A list of P unique indices (0 ≤ index < N).
        """
        return random.sample(range(N), P)
    
    @staticmethod
    def generateRandomNumber():
        """
        Generates a cryptographically secure random number.
        
        Returns:
            bytes: A random number of size M bytes.
        """
        return os.urandom(M)

    def update_vault(self, data):
        """
        Updates the vault by computing an HMAC over the concatenation of all keys.
        The HMAC result is partitioned and XORed with existing keys to refresh them.

        Args:
            data (bytes): The exchanged data used as the HMAC key.
        
        Process:
        1. Compute HMAC using `data` as the key and all concatenated keys as the message.
        2. If the HMAC output is smaller than M-byte partitions, pad it with zeros.
        3. XOR the vault keys with corresponding partitions of the HMAC output.
        """
        
        print("Updating key ...")
        
        # Compute HMAC (hashing all keys together using exchanged data as the key)
        h = hmac.new(data, b''.join(self.__keys), hashlib.sha256).digest()
        
        # Ensure proper partitioning: Pad with zeros if needed
        if len(h) % M != 0:
            h = h + b'\0' * (M - len(h) % M)
            
        # Divide HMAC output into j partitions of M bytes
        partitions = [h[i:i+M] for i in range(0, len(h), M)]
        
        # XOR each vault key with the corresponding partition (cyclic indexing)
        for i in range(len(self.__keys)):
            self.__keys[i] = bytes(a ^ b for a, b in zip(self.__keys[i], partitions[i % len(partitions)]))
