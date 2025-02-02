import time
from iot_devices import IoTDevice
from iot_server import IoTServer
from secure_vault import SecureVault

if __name__ == "__main__":
    server = IoTServer()
    server.start()

    IoTDevice(1).connect(server)
    IoTDevice(2).connect(server)

    server.join()