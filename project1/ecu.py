from frame import Frame
from can_bus import CanBus

class ECU:
    ERROR_ACTIVE = 0
    ERROR_PASSIVE = 1
    BUS_OFF = 2

    TEC = 0
    REC = 0
    status = ERROR_ACTIVE
    TECvalues = []
    RECvalues = []

    def __init__(self, name, canBus: 'CanBus', frame: 'Frame'):
        self.name = name
        self.canBus = canBus
        self.frame = frame

    def sendFrame(self):
        self.canBus.sendFrameOnBus(self.frame)

    def checkCanBusFrame(self):
        canBusFrame = self.canBus.getSendedFrame()
        ecuFrameBits = self.frame.getBits()
        if canBusFrame != ecuFrameBits:
            print(f"Mismatch detected {self.name}:\nCAN Bus Frame: {canBusFrame}\nECU Frame Bits: {ecuFrameBits}")
            self.TECincrease()

    def TECincrease(self):
        self.TEC += 8
        self.TECvalues.append(self.TEC)
        self.errorStatus()

    def errorStatus(self):
        if self.TEC > 127 or self.REC > 127:
            self.status = self.ERROR_PASSIVE
        elif self.TEC <= 127 and self.REC <= 127:
            self.status = self.ERROR_ACTIVE
        elif self.TEC > 255:
            self.status = self.BUS_OFF

    def getTEC(self):
        return self.TEC

    def getStatus(self):
        return self.status
