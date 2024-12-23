import threading
from global_clock import GlobalClock

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"
    
    def __init__(self, clock : 'GlobalClock'):
        self.lock = threading.Lock()
        
        self.current_bit = 0b1
        self.lastSendedBit = 0b1

        self.frame = []
        self.lastSendedFrame = []

        self.status = self.IDLE

        self.clock = clock

    def transmitBit(self, bit):
        # if self.status == self.IDLE:
        #     self.clock.wait()
        with self.lock:
            # print(f"recived {bit}")
            self.current_bit &= bit
            self.status = self.ACTIVE
            # self.lastSendedBit = self.current_bit

    def nextBit(self):

        if self.status == self.WAIT: # 2 cycles without new bit 
            self.lastSendedFrame = self.frame
            self.status = self.IDLE
            print("Frame to IDLE")
            return
        else:
            self.frame.append(self.current_bit)
            
        print(f"Frame recived  {self.frame}\n status {self.status}")

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
