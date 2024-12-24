import threading
from global_clock import GlobalClock

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"
    
    def __init__(self, clock : 'GlobalClock'):
        self.clock = clock
        self.lock = threading.Lock()
        self.idle_event = threading.Event()

        self.clearBus()
        
    def transmitBit(self, bit):
        with self.lock:
            # print(f"recived {bit}")
            self.status = self.ACTIVE
            self.current_bit &= bit

            self.idle_event.clear()
            self.lastSendedFrame = []

    def nextBit(self):

        if self.status == self.WAIT: # 2 cycles without new bit 
            self.lastSendedFrame = self.frame
            self.clearBus()
            return
        else:
            self.frame.append(self.current_bit)
            
        # print(f"Frame recived  {self.frame}\n status {self.status}")

        self.lastSendedBit = self.current_bit
        self.current_bit = 0b1
        self.status = self.WAIT

    def getSendedFrame(self):
        return self.lastSendedFrame
    
    def getSendedBit(self):
        return self.lastSendedBit

    def clearBus(self):
        self.current_bit = 0b1
        self.lastSendedBit = 0b1

        self.frame = []

        self.status = self.IDLE
        self.idle_event.set() 

        # print("CanBus to IDLE")

    def getStatus(self):
        return self.status
