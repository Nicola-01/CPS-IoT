import sys
import time
from iot_devices import IoTDevice
from iot_server import IoTServer
from tabulate import tabulate
from global_variables import M

"""
main.py - Entry point for the IoT authentication system.

This script initializes an IoT server and multiple IoT devices, simulating 
a real-world IoT authentication process using the Secure Vault mechanism.

Execution Flow:
1. Start the IoT server in a separate thread.
2. Simulate multiple IoT devices attempting to connect to the server.
3. Handle duplicate device connections to test authentication handling.

"""

IoTDeviceNum = 30

if __name__ == "__main__":
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
        encrypt_time, decrypt_time, sv_update_time = device.getTimings()
        timings.append((i, encrypt_time, decrypt_time, sv_update_time))
    
    # Attempt to reconnect existing devices (to test duplicate authentication)
    IoTDevice(1).connect(server)
    IoTDevice(3).connect(server)
    
    time.sleep(0.1) # Wait for authentication to complete
    
    # Calculate averages
    avg_encrypt = sum(t[1] for t in timings) / IoTDeviceNum
    avg_decrypt = sum(t[2] for t in timings) / IoTDeviceNum
    avg_sv_update = sum(t[3] for t in timings) / IoTDeviceNum

    # Print the table
    print("Timing Results, AES-128 Encryption/Decryption, SHA 512 with HMAC for SV update:")
    print("+---------+----------------+----------------+----------------+")
    print("| Device  | Encrypt Time   | Decrypt Time   | SV Update Time |")
    print("+=========+================+================+================+")

    for t in timings:
        print(f"| {t[0]:7} | {t[1]:.12f} | {t[2]:.12f} | {t[3]:.12f} |")
    print("+=========+================+================+================+")
    print(f"| Average | {avg_encrypt:<.12f} | {avg_decrypt:<.12f} | {avg_sv_update:<.12f} |")
    print("+---------+----------------+----------------+----------------+")
    
    print("Exiting program...")