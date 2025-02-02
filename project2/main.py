import time
from iot_devices import IoTDevice
from iot_server import IoTServer

if __name__ == "__main__":
    server = IoTServer()
    server.start()

    for i in range(1, 6):
        time.sleep(0.01)
        IoTDevice(i).connect(server)
    
    IoTDevice(1).connect(server)
    IoTDevice(3).connect(server)
    
    server.join()