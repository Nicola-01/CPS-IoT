import threading
from global_clock import GlobalClock

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"

    
    
    def __init__(self, clock : 'GlobalClock'):
        # self.__clock = clock
        self.__lock = threading.Lock()
        self.idleEvent = threading.Event()
        self.retransmitEvent = threading.Event()

        self.__requiredRetransmit = 0

        self.clearBus()
        
    def transmitBit(self, bit):
        with self.__lock:
            # print(f"recived {bit}")
            self.status = self.ACTIVE
            self.current_bit &= bit

            self.idleEvent.clear()
            self.retransmitEvent.clear()
            self.lastSendedFrame = []

    def nextBit(self):

        if self.__requiredRetransmit > 0 and self.status == self.IDLE:
            self.status = self.IDLE
            self.idleEvent.clear() 
            self.retransmitEvent.set()
            self.__requiredRetransmit -= 1

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
        self.idleEvent.set() 

        # print("CanBus to IDLE")

    def getStatus(self):
        return self.status
    
    def requiredRetransmitedRet(self):
        with self.__lock:
            self.__requiredRetransmit += 1
