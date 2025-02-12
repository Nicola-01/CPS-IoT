import os
import sys
import time
from iot_server import IoTServer
from iot_device import IoTDevice
from prettytable import PrettyTable

IoTDeviceNum = 10
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
    
    table = PrettyTable()
    table.field_names = ["Device ID", "Auth. (ms)"]
    for t in timings:
        table.add_row([f"{t[0]}", f"{t[1]*1000:.8f}"])
    
    table.add_divider()
    table.add_row(["Average", f"{avg_auth*1000:.8f}"])
    print(table)
    
    print("\nExiting program...")
        