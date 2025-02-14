import os
import sys
import time
from iot_server import IoTServer
from iot_device import IoTDevice
from prettytable import PrettyTable

# Number of IoT devices to simulate
IoTDeviceNum = 30

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
    for i in range(0, IoTDeviceNum + 1):
        device = IoTDevice(i)  # Create a new IoT device
        
        keyGenTime, signTime, verifyTime, authenticationTime = device.connect(server)
        timings.append((i, keyGenTime, signTime, verifyTime, authenticationTime))  # Connect the device to the server and record timing
        
    timings.pop(0)  # Remove the first device's timing results,
                    # because they are larger than the others due to the additional code update time.    
    
    # Calculate the average authentication time
    avgKeyGen = sum(t[1] for t in timings) / IoTDeviceNum
    avgSignTime = sum(t[2] for t in timings) / IoTDeviceNum
    avgVerifyTime = sum(t[3] for t in timings) / IoTDeviceNum
    avgAuth = sum(t[4] for t in timings) / IoTDeviceNum
    
    # Allow time for authentication threads to complete
    time.sleep(0.1)  
    
    # Restore stdout to display results
    sys.stdout = sys.__stdout__ 
    
    # Print the table with timing results
    print(f"\n\nTiming Results, ECC")
    
    # Create a PrettyTable to display results
    table = PrettyTable()
    table.field_names = ["Device ID", "Key Gen (ms)", "Sign (ms)" , "Verify (ms)", "" ,"Auth. (ms)"]
    for t in timings:
        table.add_row([f"{t[0]}", f"{t[1]*1000:.8f}", f"{t[2]*1000:.8f}", f"{t[3]*1000:.8f}", "", f"{t[4]*1000:.8f}"])  # Add each device's timing to the table
    
    # Add a divider and the average time to the table
    table.add_divider()
    table.add_row(["Average", f"{avgKeyGen*1000:.8f}", f"{avgSignTime*1000:.8f}", f"{avgVerifyTime*1000:.8f}", "", f"{avgAuth*1000:.8f}"])
    print(table)
    
    # Print the sum    
    print(f"ECC: {(avgKeyGen + avgSignTime + avgVerifyTime)*(10**6):.8f} us")
    
    
    print("\nExiting program...")