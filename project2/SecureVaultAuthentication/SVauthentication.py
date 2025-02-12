import os
import sys
import time
from iot_device import IoTDevice
from iot_server import IoTServer
from global_variables import *
from prettytable import PrettyTable

"""
main.py - Entry point for the IoT authentication system.

This script initializes an IoT server and multiple IoT devices, simulating 
a real-world IoT authentication process using the Secure Vault mechanism.

Execution Flow:
1. Start the IoT server in a separate thread.
2. Simulate multiple IoT devices attempting to connect to the server.
3. Handle duplicate device connections to test authentication handling.

"""

IoTDeviceNum = 1000
DEBUG_LOGS = False

if __name__ == "__main__":
    
    if(not DEBUG_LOGS):
        sys.stdout = open(os.devnull, 'w') 
    
    # Initialize and start the IoT server thread
    server = IoTServer()
    server.daemon = True
    server.start()
    
    # List to store timing results
    timings = []
    
    # Simulate multiple IoT devices attempting to connect to the server
    for i in range(1, IoTDeviceNum + 1):
        device = IoTDevice(i)
        device.connect(server)
        time.sleep(0.01) # Wait for device to connect
        encryptTime, decryptTime, SVupdateTime, authenticationTime = device.getTimings()
        timings.append((i, encryptTime, decryptTime, SVupdateTime, authenticationTime))
    
    # Attempt to reconnect existing devices (to test duplicate authentication)
    IoTDevice(1).connect(server)
    IoTDevice(3).connect(server)
    
    time.sleep(0.1) # Wait for authentication to complete
    
    # Calculate averages
    avg_encrypt = sum(t[1] for t in timings) / IoTDeviceNum
    avg_decrypt = sum(t[2] for t in timings) / IoTDeviceNum
    avg_sv_update = sum(t[3] for t in timings) / IoTDeviceNum
    avg_auth = sum(t[4] for t in timings) / IoTDeviceNum

    sys.stdout = sys.__stdout__ 

    # Print the table
    SVupdate = "SHA-512 with HMAC" if SHA512_WITH_HMAC else "SHA-512"
    print(f"\n\nTiming Results, AES-{8*M} as Encryption/Decryption, {SVupdate} for secure valult update:")
    
    table = PrettyTable()
    table.field_names = ["Device ID", "Encrypt (ms)", "Decrypt (ms)", "SV Update (ms)", "Auth. (ms)"]
    
    for t in timings:
        table.add_row([f"{t[0]}", f"{t[1]*1000:.8f}", f"{t[2]*1000:.8f}", f"{t[3]*1000:.8f}", f"{t[4]*1000:.8f}"])

    table.add_divider()
    table.add_row(["Average", f"{avg_encrypt*1000:.8f}", f"{avg_decrypt*1000:.8f}", f"{avg_sv_update*1000:.8f}", f"{avg_auth*1000:.8f}"])
    print(table)
        
    print(f"Decrypt avg time + Encrypt avg time + SV Update avg time: {(avg_decrypt*1000 + avg_encrypt*1000 + avg_sv_update*1000):.8f} ms")
    
    print("\nExiting program...")