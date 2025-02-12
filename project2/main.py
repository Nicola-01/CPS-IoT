import sys
import time
from iot_devices import IoTDevice
from iot_server import IoTServer
from tabulate import tabulate

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

    # Print table
    table_data = [["Device", "Encrypt Time", "Decrypt Time", "SV Update Time"]]
    for t in timings:
        table_data.append([t[0], f"{t[1]:.10f}", f"{t[2]:.10f}", f"{t[3]:.10f}"])
    table_data.append(["═" * 7, "═" * 13, "═" * 13, "═" * 13])
    table_data.append(["Average", f"{avg_encrypt:.10f}", f"{avg_decrypt:.10f}", f"{avg_sv_update:.10f}"])
    print(tabulate(table_data, headers="firstrow", tablefmt="fancy_grid"))
    
    print("Exiting program...")