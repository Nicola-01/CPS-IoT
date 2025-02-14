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

# Number of IoT devices to simulate
IoTDeviceNum = 30

# Flag to enable or disable debug logs
DEBUG_LOGS = False

if __name__ == "__main__":
    # Suppress logs if DEBUG_LOGS is False
    if not DEBUG_LOGS:
        sys.stdout = open(os.devnull, 'w') 
    
    # Initialize and start the IoT server thread
    server = IoTServer()
    server.daemon = True  # Daemonize the server thread to allow program exit
    server.start()
    
    # List to store timing results for each device
    timings = []
    
    # Simulate multiple IoT devices attempting to connect to the server
    for i in range(0, IoTDeviceNum + 1):
        device = IoTDevice(i)  # Create a new IoT device
        device.connect(server)  # Connect the device to the server
        time.sleep(0.01)  # Wait for the device to connect
        # Retrieve timing information for encryption, decryption, secure vault update, and authentication
        encryptTime, decryptTime, SVupdateTime, authenticationTime = device.getTimings()
        # Append the timing results to the list
        timings.append((i, encryptTime, decryptTime, SVupdateTime, authenticationTime))
    
    timings.pop(0)  # Remove the first device's timing results,
                    # because they are larger than the others due to the additional code update time.
    
    # Restore stdout to display results
    sys.stdout = sys.__stdout__ 
    
    # Attempt to reconnect existing devices (to test duplicate authentication)
    IoTDevice(1).connect(server)  # Reconnect device 1
    
    # Wait for all authentication processes to complete
    time.sleep(0.1)
    
    # Calculate average times for encryption, decryption, secure vault update, and authentication
    avgEncrypt = sum(t[1] for t in timings) / IoTDeviceNum
    avgDecrypt = sum(t[2] for t in timings) / IoTDeviceNum
    avgSVupdate = sum(t[3] for t in timings) / IoTDeviceNum
    avgAuth = sum(t[4] for t in timings) / IoTDeviceNum


    # Print the table with timing results
    SVupdate = "SHA-512 with HMAC" if SHA512_WITH_HMAC else "SHA-512"
    print(f"\n\nTiming Results, AES-{8*M} as Encryption/Decryption, {SVupdate} for secure vault update:")
    
    # Create a PrettyTable to display the results
    table = PrettyTable()
    table.field_names = ["Device ID", "Encrypt (ms)", "Decrypt (ms)", "SV Update (ms)", "" , "Auth. (ms)"]
    
    # Add each device's timing results to the table
    for t in timings:
        table.add_row([f"{t[0]}", f"{t[1]*1000:.8f}", f"{t[2]*1000:.8f}", f"{t[3]*1000:.8f}", "" , f"{t[4]*1000:.8f}"])

    # Add a divider and the average times to the table
    table.add_divider()
    table.add_row(["Average", f"{avgEncrypt*1000:.8f}", f"{avgDecrypt*1000:.8f}", f"{avgSVupdate*1000:.8f}", "", f"{avgAuth*1000:.8f}"])
    print(table)
    
    aesAvg = (avgEncrypt+avgDecrypt)/2
    print(f"\nAES-{8*M}: {aesAvg*(10**6):.3f} us")
    print(f"{SVupdate}: {avgSVupdate*(10**6):.3f} us")
        
    print(f"\nSV algorithm: AES-{8*M} * 2 + SV Update = {(aesAvg*2 + avgSVupdate)*(10**6):.3f} us")
    print(f"Single Rotating Password: AES-{8*M} * 3 = {(aesAvg*3)*(10**6):.3f} us")
    
    # Indicate program exit
    print("\nExiting program...")