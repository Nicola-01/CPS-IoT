import copy
import threading
from iot_device import IoTDevice
from secure_vault import SecureVault
from crypto_utils import encrypt, decrypt
from global_variables import M

class IoTServer(threading.Thread):
    """
    IoT Server that listens for device connections and manages authentication
    using a secure vault.
    """


    def __init__(self):
        """
        Initializes the IoT server.
        """

        super().__init__()
        self.__lock = threading.Lock()
        self.__condition = threading.Condition(self.__lock)  # Condition variable

        self.__authRequests = [] # List of IoTDevice objects
        self.__pairedDevices = [] # List of device IDs that have been paired
        self.__pendingDevices = [] # List of device IDs that are pending


    def run(self):
        """
        Main server loop that listens for authentication requests.
        """

        print("Server listening...\n")
        while True:
            with self.__condition:
                while len(self.__pendingDevices) == 0:  # Wait until a device is pending
                   self.__condition.wait()

                # Get the first pending device
                deviceID, sessionID = self.__pendingDevices.pop(0)
                
                # print(f"   D{deviceID} start authentication process")

                request = self.__getRequests(deviceID)
                device = request['device']
                secureVault = request['secureVault']

                # Generate server's challenge
                c1 = SecureVault.generateChallenge()
                r1 = SecureVault.generateRandomNumber()
                m2 = (c1, r1)

                k1 = secureVault.getKey(c1)
                print(f"   Server sends M2 to D{deviceID}: {m2}")
                m3, _ = decrypt(k1, device.sendMessage2(m2))

                # Parse M3 message
                r1_received, t1, c2, r2 = self.__parseM3(m3)

                # Verify received challenge response
                if r1_received != r1:
                    print(f"Authentication failed at M3 verification for device {deviceID}.")
                    return
                print(f"   Server: D{deviceID} successfully verified M3")

                # Generate k2, k3, and t2
                k2 = secureVault.getKey(c2)
                k3 = bytes(a ^ b for a, b in zip(k2, t1))
                t2 = SecureVault.generateRandomNumber()

                # Generate M4 message
                payload = r2 + t2
                m4,_ = encrypt(k3, payload)

                # Authenticate device
                print(f"   Server sends M4 to D{deviceID}: {m4}")
                if(device.sendMessage4(m4)):
                    sessionKey = bytes(a ^ b for a, b in zip(t2, t1))
                    print(f"   Session key (Server) for Device {deviceID}: {sessionKey.hex()}")

                    # Update secure vault
                    print(f"   Server updates vault with session key for D{deviceID}")
                    secureVault.update_vault(sessionKey)

                    # Add device to paired list in a thread-safe way
                    self.__pairedDevices.append(deviceID)
                    # print(f"Device {deviceID} successfully authenticated.")

    def startAuthentication(self, m1: tuple):
        """
        Adds a device to the authentication queue.

        Args:
            m1 (tuple): (deviceID, sessionID)
        """

        deviceID, sessionID = m1

        with self.__condition:
            
            # with self.__lock:
            if int(deviceID) in map(int, self.__pairedDevices):
                print(f"Server refuse Device {deviceID}, already connected")
                return False
            
            # print(f"   D{deviceID} added to pending devices")
            self.__pendingDevices.append((deviceID, sessionID))
            self.__condition.notify()


    def __parseM3(self, msg: bytes) -> tuple:
        """
        Parses M3 message received from the IoT device.

        Args:
            msg (bytes): Decrypted M3 message.

        Returns:
            tuple: Extracted values (r1, t1, c2, r2).
        """

        r1 = msg[:M]
        t1 = msg[M:M*2]
        c2 = msg[M*2:len(msg)-M]
        r2 = msg[-M:]

        return r1, t1, c2, r2

    def setUpConnection(self, device : IoTDevice) -> SecureVault:
        """
        Registers a new IoT device.

        Args:
            device (IoTDevice): The IoT device to register.

        Returns:
            SecureVault: A copy of the device's secure vault.
        """

        with self.__lock:
            sv = SecureVault()
            self.__authRequests.append({
                'deviceID': device.getID(),
                'device': device,
                'secureVault': sv
            })
            return copy.deepcopy(sv)

    def __getRequests(self, deviceID: int) -> IoTDevice:
        """
        Retrieves a registered IoT device.

        Args:
            deviceID (int): Device ID.

        Returns:
            IoTDevice: The corresponding IoT device, or None if not found.
        """
        for device in self.__authRequests:
            if device['deviceID'] == deviceID:
                return device
        return None