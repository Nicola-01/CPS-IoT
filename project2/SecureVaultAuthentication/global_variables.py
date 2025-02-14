N = 16   # Number of keys in the secure vault (Max: 256)
M = 16  # Size of each key in bytes (Valid values: 16, 24, or 32 for AES)
P = 6  # Number of keys used in each authentication challenge (Must be <= N)

SHA512_WITH_HMAC = True  # Set to True to use HMAC-SHA512 for updating the vault