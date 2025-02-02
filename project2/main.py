import time
import threading

from iot_devices import IoTDevice
from iot_server import IoTServer
from secure_vault import SecureVault

if __name__ == "__main__":
    server = IoTServer()
    
    server.start()
    
    device = IoTDevice(1, server)
    device.connect(server)
    
    server.join()
    