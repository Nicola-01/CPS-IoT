from frame import Frame
from can_bus import CanBus
from global_clock import GlobalClock
import time

class ECU:
    """
    Represents an Electronic Control Unit (ECU) in a CAN bus system.

    Attributes:
        ERROR_ACTIVE: The ECU is in the active error state.
        ERROR_PASSIVE: The ECU is in the passive error state.
        BUS_OFF: The ECU is in the bus-off state and cannot send messages.

        COMPLITED: Frame transmission completed successfully.
        BIT_ERROR: A bit error was detected during transmission.
        STUFF_ERROR: A stuffing error was detected during transmission.
        LOWER_FRAME_ID: Another ECU has a lower frame ID (priority conflict).
    """

    # ECU status
    ERROR_ACTIVE = "ERROR_ACTIVE"
    ERROR_PASSIVE = "ERROR_PASSIVE"
    BUS_OFF = "BUS_OFF"

    # Transmission status
    COMPLITED = "COMPLITED"
    BIT_ERROR = "BIT_ERROR"
    STUFF_ERROR = "STUFF_ERROR"
    LOWER_FRAME_ID = "LOWER_FRAME_ID"

    # Error flags
    __ERROR_ACTIVE_FLAG = [0b0] * 6  # Error flag for active state
    __ERROR_PASSIVE_FLAG = [0b1] * 6  # Error flag for passive state


    def __init__(self, name: str, canBus: 'CanBus', clock : 'GlobalClock'):
        """
        Initialize an ECU instance.

        Args:
            name (str): Name of the ECU.
            canBus (CanBus): CAN bus instance the ECU is connected to.

            clock (GlobalClock): Clock for synchronization.
        """
        
        self.name = name
        self.__canBus = canBus
        self.__clock = clock

        self.__TEC = 0  # Transmit Error Counter
        self.__REC = 0  # Receive Error Counter (not fully used)
        self.__status = self.ERROR_ACTIVE # ECU start status
        self.__TECvalues = [[0, time.time()]]  # Store TEC changes over time


    def sendFrame(self, frame : 'Frame') -> str:
        """
        Transmit a frame over the CAN bus.

        Args:
            frame (Frame): Frame to be transmitted.
        
        Returns:
            str: Transmission status (COMPLITED, LOWER_FRAME_ID, BIT_ERROR, or STUFF_ERROR).
        """
        
        if self.__status == self.BUS_OFF: # if bus off, do not send
            return
        
        i = 0 # bit index
        frameBits = frame.getBits() # get frame bits
        recivedBit = [] # store bits recived from canbus

        while True:
            self.__canBus.transmitBit(frameBits[i]) # Send a bit
            self.__canBus.waitWaitStatus() # Wait for arbitration to complete
            lastSendedBit = self.__canBus.getSendedBit() # Get the bit transmitted on the bus
            recivedBit.append(lastSendedBit)

            # Check the ID field (first 11 bits)
            if 1 <= i <= 11:
                if frameBits[i] > lastSendedBit:
                    return self.LOWER_FRAME_ID # Another ECU has a lower ID, stop transmission

            # Check for bit errors
            elif i > 11:
                if frameBits[i] != lastSendedBit: # detect bit error
                    self.__sendError()
                    self.__TECincrease()
                    return self.BIT_ERROR
            
            # Check for stuffing rule violations
            if self.__checkStuffRule(recivedBit):
                self.__sendError()
                self.__TECincrease()
                return self.STUFF_ERROR
                
            i += 1
            if i == len(frameBits): # Transmission completed
                self.__TECdecrease()
                return self.COMPLITED
            
            self.__clock.wait() # Sync
    
    def __TECincrease(self):
        """Increase the Transmit Error Counter (TEC) and update the ECU's state."""
        self.__TEC += 8
        self.__TECvalues.append([self.__TEC, time.time()])
        self.errorStatus()

    def __TECdecrease(self):
        """Decrease the Transmit Error Counter (TEC) and update the ECU's state."""
        if self.__TEC > 0:
            self.__TEC -= 1
        self.__TECvalues.append([self.__TEC, time.time()])
        self.errorStatus()

    # def __RECincrease(self):
    #     if not self.checkBound(self.__REC):
    #         return
    #     self.__REC += 8
    #     self.__RECvalues.append([self.__REC, time.time()])
    #     self.errorStatus()

    # def __RECdecrease(self):
    #     if not self.checkBound(self.__REC):
    #         return
    #     self.__REC -= 1
    #     self.__RECvalues.append([self.__REC, time.time()])
    #     self.errorStatus()

    def errorStatus(self):
        """Update the ECU's error state based on TEC and REC values."""
        if self.__TEC > 127 or self.__REC > 127:
            self.__status = self.ERROR_PASSIVE
        if self.__TEC <= 127 and self.__REC <= 127:
            self.__status = self.ERROR_ACTIVE
        if self.__TEC > 255:
            self.__status = self.BUS_OFF

    def getStatus(self) -> str:
        """Get the current error state of the ECU."""
        return self.__status
    
    def getTEC(self) -> int:
        """Get the current Transmit Error Counter (TEC)."""
        return self.__TEC
    
    def getTECs(self) -> list:
        """Get the history of TEC values."""
        return self.__TECvalues
    
    # def getRECs(self):
    #     return self.__RECvalues
    
    def __checkStuffRule(self, recivedBit : list) -> bool:
        """
        Check if the stuffing rule is violated.

        Args:
            recivedBit (list): Received bits to check.

        Returns:
            bool: True if stuffing rule is violated, False otherwise.
        """
        
        if len(recivedBit) < 6:
            return False

        last_six_bits = recivedBit[-6:]
        return all(bit == 0 for bit in last_six_bits) or all(bit == 1 for bit in last_six_bits)
    
    def __sendError(self):
        """
        Send an error flag on the CAN bus based on the ECU's error state.
        """
        
        error_flag = self.__ERROR_ACTIVE_FLAG if self.__status == self.ERROR_ACTIVE else self.__ERROR_PASSIVE_FLAG
        for bit in error_flag:
            self.__canBus.transmitBit(bit)
            self.__canBus.waitWaitStatus()