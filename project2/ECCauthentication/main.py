import os
import sys
import time
from iot_server import IoTServer
from iot_device import IoTDevice

IoTDeviceNum = 1000
DEBUG_LOGS = False

if __name__ == "__main__":
    
    if(not DEBUG_LOGS):
        sys.stdout = open(os.devnull, 'w') 
        
    # Initialize and start the IoT server thread
    server = IoTServer()
    server.daemon = True
    server.start()
    timings = []
    
    # Simulate multiple IoT devices attempting to connect to the server
    for i in range(1, IoTDeviceNum + 1):
        device = IoTDevice(i)
        timings.append((i, device.connect(server)))
        
    avg_auth = sum(t[1] for t in timings) / IoTDeviceNum
    
    time.sleep(0.1)  # Allow time for authentication threads to complete
    
    sys.stdout = sys.__stdout__ 
    
        # Print the table
    print(f"\n\nTiming Results, ECC")
    print("+---------+----------------+")
    print("| Device  | Authentication |")
    print("+=========+================+")

    for t in timings:
        print(f"| {t[0]:7} | {t[1]:.12f} |")
    print("+=========+================+")
    print(f"| Average | {avg_auth:.12f} |")
    print("+---------+----------------+")
    
    print("Exiting program...")
        