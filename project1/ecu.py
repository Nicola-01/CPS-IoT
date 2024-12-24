from frame import Frame
from can_bus import CanBus
from global_clock import GlobalClock

import matplotlib.pyplot as plt

class ECU:

    # ECU status
    ERROR_ACTIVE = "ERROR_ACTIVE"
    ERROR_PASSIVE = "ERROR_PASSIVE"
    BUS_OFF = "BUS_OFF"

    # Transmission status
    COMPLITED = "COMPLITED"
    DIFFERENT_ID = "DIFFERENT_ID"
    BIT_ERROR = "BIT_ERROR"
    STUFF_ERROR = "STUFF_ERROR"

    __ERROR_ACTIVE_FLAG = [0b0] * 6
    __ERROR_PASSIVE_FLAG = [0b1] * 6

    __TEC = 0
    __REC = 0
    __status = ERROR_ACTIVE
    __TECvalues = [0]
    __RECvalues = [0]

    def __init__(self, name, canBus: 'CanBus', frame: 'Frame', clock : 'GlobalClock'):
        self.name = name
        self.canBus = canBus
        self.frame = frame
        self.clock = clock

    def sendFrame(self):

        recivedBit = []

        if self.__status == self.BUS_OFF:
            return

        i = 0

        frameBits = self.frame.getBits()

        while True:
            self.canBus.transmitBit(frameBits[i])
            print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}\n")
            
            self.clock.wait()
            self.clock.wait()
            lastSendedBit = self.canBus.getSendedBit()

            recivedBit.append(lastSendedBit)
            if self.__checkStuffRule(recivedBit):
                self.__sendError()
                self.__TECincrease()
                return self.STUFF_ERROR

            print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n")

            if i >= 1 and i <= 11: # check the id
                if frameBits[i] != lastSendedBit:
                    return self.DIFFERENT_ID # different id, stop transmission

            elif i > 11:
                if frameBits[i] != lastSendedBit:
                    self.__sendError()
                    self.__TECincrease()
                    # TODO: retransission
                    self.__TECdecrease()
                    return self.BIT_ERROR
                
            i += 1
            if len(frameBits) == i:
                self.__TECdecrease()
                return self.COMPLITED
            self.clock.wait()
    
    def checkBound(self, errorCounter):
        return errorCounter >= 0 # and errorCounter <= 300

    def __TECincrease(self):
        if not self.checkBound(self.__TEC):
            return
        self.__TEC += 8
        self.__TECvalues.append(self.__TEC)
        self.errorStatus()

    def __TECdecrease(self):
        if not self.checkBound(self.__TEC):
            return
        self.__TEC -= 1
        self.__TECvalues.append(self.__TEC)
        self.errorStatus()

    def __RECincrease(self):
        if not self.checkBound(self.__REC):
            return
        self.__REC += 8
        self.__RECvalues.append(self.__REC)
        self.errorStatus()

    def __RECdecrease(self):
        if not self.checkBound(self.__REC):
            return
        self.__REC -= 1
        self.__RECvalues.append(self.__REC)
        self.errorStatus()

    def errorStatus(self):
        if self.__TEC > 127 or self.__REC > 127:
            self.__status = self.ERROR_PASSIVE
        if self.__TEC <= 127 and self.__REC <= 127:
            self.__status = self.ERROR_ACTIVE
        if self.__TEC > 20:
            self.__status = self.BUS_OFF

    def getTEC(self):
        return self.__TEC

    def getStatus(self):
        return self.__status
    
    def getTECs(self):
        return self.__TECvalues
    
    def getRECs(self):
        return self.__RECvalues
    
    def __checkStuffRule(self, recivedBit : list):
        if len(recivedBit) < 6:
            return False

        sum = 0
        for bit in recivedBit[-6:][::-1]: # check only last 6
            sum += bit
        
        return (sum == 0 or sum == 6) # 6 bits to 0 or 6 bits to 1
    
    def __sendError(self):
        if self.__status == self.ERROR_ACTIVE:
            error_flag = self.__ERROR_ACTIVE_FLAG
        else: 
            error_flag = self.__ERROR_PASSIVE_FLAG

        print(f"{self.name} flag sended {error_flag}")

        for bit in error_flag:
            self.canBus.transmitBit(bit)
            self.clock.wait()
            self.clock.wait()
            self.clock.wait()