import threading
import time
from global_clock import GlobalClock

class CanBus:
    """
    Simulates a CAN bus communication system.

    Attributes:
        IDLE: Bus is idle and ready for new transmissions.
        WAIT: Bus is waiting for the next bit.
        ACTIVE: A transmission is currently active on the bus.
    """
    
    IDLE = "IDLE"
    WAIT = "WAIT"
    ACTIVE = "ACTIVE"
    
    def __init__(self, clock : 'GlobalClock'):
        """
        Initializes the CAN bus.

        Args:
            clock (GlobalClock): Global clock for timing synchronization.
        """
        
        self.__clock = clock
        self.__lock = threading.Lock() # Ensure thread-safe operations
        self.__count = 0
        self.__conseutiveIdle = 0 # Track consecutive idle states
        
        # Events for synchronization
        self.__idleEvent = threading.Event()
        self.__waitEvent = threading.Event()
        self.__frameCountEvent = threading.Event()
        
        # Not used in this implementation, but could be useful for retransmissions
        self.__retransmitEvent = threading.Event() 
        self.__requiredRetransmit = 0
        
        self.__lastSendedFrame = [] # Store the last frame sent
        self.clearBus()
        
    def transmitBit(self, bit: int):
        """
        Transmit a single bit on the bus.

        Args:
            bit (int): The bit to transmit (0 or 1).
        """
        
        with self.__lock:
            self.__status = self.ACTIVE
            self.__current_bit &= bit

            # Clear events
            self.__idleEvent.clear()
            self.__waitEvent.clear()
            self.__frameCountEvent.clear()

    def process(self):        
        with self.__lock:
            """
            Store the current bit in the frame and update the bus status.
            """

            # CanBus to IDLE status
            if self.__status == self.WAIT:  # Two cycles without new bits
                self.__lastSendedFrame = self.__frame
                self.clearBus()
                self.__count+=1
                self.__frameCountEvent.set()
            
            # CanBus to WAIT status
            elif self.__status == self.ACTIVE:
                self.__frame.append(self.__current_bit)
                
                # Add current bit to frame
                self.__lastSendedBit = self.__current_bit
                self.__current_bit = 0b1  # Reset current bit
                
                self.__status = self.WAIT
                self.__waitEvent.set()
                
            elif self.__status == self.IDLE:  # Handle idle state
                # if two consecutive idle states, increment frame count,
                # frame count is used for periodic sending of frames by the ECUs 
                self.__conseutiveIdle += 1
                if self.__conseutiveIdle == 2:
                    self.__count+=1
                    self.__frameCountEvent.set()
                    self.__conseutiveIdle = 0
                else:
                    self.__frameCountEvent.clear()
                self.__lastSendedFrame = None # reset last frame

    def getSendedFrame(self) -> list:
        """Returns the last transmitted frame."""
        return self.__lastSendedFrame
    
    def getSendedBit(self) -> int:
        """Returns the last transmitted bit."""
        return self.__lastSendedBit

    def clearBus(self):
        """
        Resets the bus to its default idle state.
        Clears current frame data and updates status to IDLE.
        """
        
        self.__current_bit = 0b1
        self.__lastSendedBit = 0b1

        self.__frame = []

        self.__status = self.IDLE
        self.__idleEvent.set() 
        self.__waitEvent.clear()

    def getStatus(self) -> str:
        """Returns the current bus status."""
        return self.__status
    
    def requiredRetransmitedRet(self):
        """Increments the retransmission counter."""
        with self.__lock:
            self.__requiredRetransmit += 1
            
    def getCount(self) -> int:
        """Returns the current frame count."""
        return self.__count
    
    def waitIdleStatus(self):
        """Waits until the bus status is IDLE."""
        while self.__status != self.IDLE:
            self.__idleEvent.wait()
        
    def waitWaitStatus(self):
        """Waits until the bus status is WAIT."""
        self.__waitEvent.wait()
        
    def waitFrameCountIncreese(self):
        """Waits for the frame count to increase."""
        self.__frameCountEvent.wait()
        
    # I tried to avoid to use this method, since is not correct that the CanBus inform the ECU when to send a frame 
    def waitFrameCountMultiple(self, period):
        """
        Waits until the frame count is a multiple of a given period.

        Args:
            period (int): The period to check against.

        Returns:
            int: The current frame count.
        """
        while self.__count % period != 0: # wait until the frame count is a multiple of period
            time.sleep(0.001)
        return self.__count
            
    # I tried to avoid to use this method, since is not correct that the CanBus inform the ECU when to send a frame 
    def waitFrameCount(self, frameNumber):
        """
        Waits until the frame count reaches a specified number.

        Args:
            frameNumber (int): The target frame count.
        """
        while self.__count < frameNumber: # wait until the frame count is equal to frameNumber
            time.sleep(0.001)
