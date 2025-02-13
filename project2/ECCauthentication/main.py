import os
import sys
import time
from iot_server import IoTServer
from iot_device import IoTDevice
from prettytable import PrettyTable

# Number of IoT devices to simulate
IoTDeviceNum = 1000

# Flag to enable or disable debug logs
DEBUG_LOGS = False

if __name__ == "__main__":
    # Redirect stdout to suppress logs if DEBUG_LOGS is False
    if not DEBUG_LOGS:
        sys.stdout = open(os.devnull, 'w') 
        
    # Initialize and start the IoT server thread
    server = IoTServer()
    server.daemon = True  # Daemonize the server thread to allow program exit
    server.start()
    
    # List to store timing results for each device
    timings = []
    
    # Simulate multiple IoT devices attempting to connect to the server
    for i in range(1, IoTDeviceNum + 1):
        device = IoTDevice(i)  # Create a new IoT device
        timings.append((i, device.connect(server)))  # Connect the device to the server and record timing
        
    # Calculate the average authentication time
    avg_auth = sum(t[1] for t in timings) / IoTDeviceNum
    
    # Allow time for authentication threads to complete
    time.sleep(0.1)  
    
    # Restore stdout to display results
    sys.stdout = sys.__stdout__ 
    
    # Print the table with timing results
    print(f"\n\nTiming Results, ECC")
    
    # Create a PrettyTable to display results
    table = PrettyTable()
    table.field_names = ["Device ID", "Auth. (ms)"]
    for t in timings:
        table.add_row([f"{t[0]}", f"{t[1]*1000:.8f}"])  # Add each device's timing to the table
    
    # Add a divider and the average time to the table
    table.add_divider()
    table.add_row(["Average", f"{avg_auth*1000:.8f}"])
    print(table)
    
    print("\nExiting program...")