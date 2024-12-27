import threading
from global_clock import GlobalClock

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"
    __count = 0
    
    def __init__(self, clock : 'GlobalClock'):
        self.__clock = clock
        self.__lock = threading.Lock()
        self.idleEvent = threading.Event()
        self.retransmitEvent = threading.Event()

        self.__requiredRetransmit = 0

        self.__lastSendedFrame = []
        self.clearBus()
        
    def transmitBit(self, bit):
        with self.__lock:
            # print(f"recived {bit}")
            self.status = self.ACTIVE
            self.current_bit &= bit

            self.idleEvent.clear()
            self.retransmitEvent.clear()

    def nextBit(self):
        with self.__lock:
            if self.__requiredRetransmit > 0 and self.status == self.IDLE:
                print("---CANBUS RETRANSMITION---")
                self.idleEvent.clear() 
                self.retransmitEvent.set()
                self.__requiredRetransmit -= 1
                # self.__clock.wait()

            if self.status == self.WAIT: # 2 cycles without new bit, transmiton finished
                self.__lastSendedFrame = self.frame
                self.__count+=1
                self.clearBus()
                # print("---CANBUS IDLE---")
                return
            else:
                self.frame.append(self.current_bit)
                
            # print(f"Frame recived  {self.frame}\n status {self.status}")

            self.__lastSendedBit = self.current_bit
            self.current_bit = 0b1
            self.status = self.WAIT

    def getSendedFrame(self):
        return self.__lastSendedFrame
    
    def getSendedBit(self):
        return self.__lastSendedBit

    def clearBus(self):
        self.current_bit = 0b1
        self.__lastSendedBit = 0b1

        self.frame = []

        self.status = self.IDLE
        self.idleEvent.set() 

    def getStatus(self):
        return self.status
    
    def requiredRetransmitedRet(self):
        with self.__lock:
            self.__requiredRetransmit += 1

    def getCount(self):
        return self.__count
