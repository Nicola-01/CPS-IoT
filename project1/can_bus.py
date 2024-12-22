import threading
from frame import Frame

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"
    
    def __init__(self):
        self.lock = threading.Lock()
        
        self.current_bit = 0b1
        self.lastSendedBit = 0b1

        self.frame = []
        self.lastSendedFrame = []

        self.status = self.IDLE

    def transmitBit(self, bit):
        with self.lock:
            print(f"recived {bit}")
            self.current_bit &= bit
            self.status = self.ACTIVE
            # self.lastSendedBit = self.current_bit

    def nextBit(self):

        print(f"Frame recived  {self.frame}\n status {self.status}")

        if self.status == self.WAIT: # 2 cycles without new bit 
            self.lastSendedFrame = self.frame
            self.status = self.IDLE
            return
        else:
            self.frame.append(self.current_bit)
            

        self.lastSendedBit = self.current_bit
        self.current_bit = 0b1
        self.status = self.WAIT

    def getSendedFrame(self):
        return self.lastSendedFrame
    
    def getSendedBit(self):
        return self.lastSendedBit

    def clearBus(self):
        self.current_bit = 0b1
        self.frames = []

    def getStatus(self):
        return self.status


    # def removeInvalidFrames(self):
    #     """Rimuove i frame con SOF diverso da 0b0."""
    #     self.frames = [frame for frame in self.frames if frame.SOF == 0b0]

    # def getLowerID(self):
    #     return min(frame.ID for frame in self.frames)

    # def onlyFramesWithID(self, ID):
    #     self.frames = [frame for frame in self.frames if frame.ID == ID]
