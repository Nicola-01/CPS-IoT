import sys
import time
from iot_devices import IoTDevice
from iot_server import IoTServer

"""
main.py - Entry point for the IoT authentication system.

This script initializes an IoT server and multiple IoT devices, simulating 
a real-world IoT authentication process using the Secure Vault mechanism.

Execution Flow:
1. Start the IoT server in a separate thread.
2. Simulate multiple IoT devices attempting to connect to the server.
3. Handle duplicate device connections to test authentication handling.

"""

if __name__ == "__main__":
    # Initialize and start the IoT server thread
    server = IoTServer()
    server.daemon = True
    server.start()
    
    # Simulate multiple IoT devices attempting to connect to the server
    for i in range(1, 2):
        IoTDevice(i).connect(server)
        time.sleep(0.01)
    
    # Attempt to reconnect existing devices (to test duplicate authentication)
    IoTDevice(1).connect(server)
    IoTDevice(3).connect(server)
    
    
    time.sleep(1) # Wait for authentication to complete
    print("Exiting program...")