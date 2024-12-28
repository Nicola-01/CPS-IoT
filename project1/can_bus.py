import threading
from global_clock import GlobalClock

class CanBus:
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    WAIT = "WAIT"

    
    
    def __init__(self, clock : 'GlobalClock'):
        self.__clock = clock
        self.__lock = threading.Lock()
        self.__count = 0
        self.__conseutiveIdle = 0
        self.__idleEvent = threading.Event()
        self.__waitEvent = threading.Event()
        self.__frameCountEvent = threading.Event()
        self.__retransmitEvent = threading.Event()

        self.__requiredRetransmit = 0

        self.__lastSendedFrame = []
        self.clearBus()
        
    def transmitBit(self, bit):
        with self.__lock:
            # print(f"recived {bit}")
            self.__status = self.ACTIVE
            self.__current_bit &= bit

            self.__idleEvent.clear()
            self.__waitEvent.clear()
            self.__frameCountEvent.clear()
            # self.retransmitEvent.clear()

    def nextBit(self):        
        with self.__lock:
            # print("CanBus nextBit")
            # if self.__requiredRetransmit > 0 and self.status == self.IDLE:
            #     print("---CANBUS RETRANSMITION---")
            #     self.idleEvent.clear() 
            #     self.retransmitEvent.set()
            #     self.__requiredRetransmit -= 1
                # self.__clock.wait()

            if self.__status == self.WAIT: # 2 cycles without new bit 
                self.__lastSendedFrame = self.__frame
                self.clearBus()
                self.__count+=1
                self.__frameCountEvent.set()
            
            elif self.__status == self.ACTIVE:
                self.__frame.append(self.__current_bit)
                
                self.__lastSendedBit = self.__current_bit
                self.__current_bit = 0b1
                self.__status = self.WAIT
                self.__waitEvent.set()
                # print("CanBus to WAIT")
                
            elif self.__status == self.IDLE:
                self.__conseutiveIdle += 1
                if self.__conseutiveIdle == 2:
                    self.__count+=1
                    self.__frameCountEvent.set()
                    self.__conseutiveIdle = 0
                else:
                    self.__frameCountEvent.clear()


                self.__lastSendedFrame = None
                # print("CanBus in IDLE")
            # print(f"CanBus __count: {self.__count}\t status: {self.__status} conseutiveIdle: {self.__conseutiveIdle}")

    def getSendedFrame(self):
        return self.__lastSendedFrame
    
    def getSendedBit(self):
        return self.__lastSendedBit

    def clearBus(self):
        self.__current_bit = 0b1
        self.__lastSendedBit = 0b1

        self.__frame = []

        self.__status = self.IDLE
        self.__idleEvent.set() 
        self.__waitEvent.clear()

        # print("CanBus to IDLE")

    def getStatus(self):
        return self.__status
    
    def requiredRetransmitedRet(self):
        with self.__lock:
            self.__requiredRetransmit += 1
            
    def getCount(self):
        return self.__count
    
    def waitIdleStatus(self):
        self.__idleEvent.wait()
        
    def waitWaitStatus(self):
        self.__waitEvent.wait()
        
    def waitFrameCountIncreese(self):
        self.__frameCountEvent.wait()
        
    def waitFrameCountMultiple(self, period):
        while self.__count % period != 0:
            self.__clock.wait()
            self.__frameCountEvent.wait()
