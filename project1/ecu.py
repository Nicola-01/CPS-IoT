from frame import Frame
from can_bus import CanBus
from global_clock import GlobalClock
import time

import matplotlib.pyplot as plt

class ECU:

    # ECU status
    ERROR_ACTIVE = "ERROR_ACTIVE"
    ERROR_PASSIVE = "ERROR_PASSIVE"
    BUS_OFF = "BUS_OFF"

    # Transmission status
    COMPLITED = "COMPLITED"
    LOWER_FRAME_ID = "LOWER_FRAME_ID"
    BIT_ERROR = "BIT_ERROR"
    STUFF_ERROR = "STUFF_ERROR"

    __ERROR_ACTIVE_FLAG = [0b0] * 6
    __ERROR_PASSIVE_FLAG = [0b1] * 6

    def __init__(self, name, canBus: 'CanBus', frame: 'Frame', clock : 'GlobalClock', start : float):
        self.name = name
        self.__canBus = canBus
        self.__frame = frame
        self.__clock = clock
        self.__start = start

        self.__TEC = 0
        self.__REC = 0
        self.__status = self.ERROR_ACTIVE
        self.__TECvalues = [[0,0]]
        self.__RECvalues = [[0,0]]

    def sendFrame(self):

        recivedBit = []

        if self.__status == self.BUS_OFF:
            return

        i = 0

        frameBits = self.__frame.getBits()

        while True:
            self.__canBus.transmitBit(frameBits[i])
            # print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}\n")
            
            self.__clock.wait()
            self.__clock.wait()
            lastSendedBit = self.__canBus.getSendedBit()

            recivedBit.append(lastSendedBit)
            if self.__checkStuffRule(recivedBit):
                self.__sendError()
                self.__TECincrease()
                return self.STUFF_ERROR

            # print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n")
            # print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n")

            if i >= 1 and i <= 11: # check the id
                if frameBits[i] > lastSendedBit:
                    return self.LOWER_FRAME_ID # different id, stop transmission

            elif i > 11:
                if frameBits[i] != lastSendedBit:
                    # if(self.__TEC>=120):
                    #     print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n")
                    self.__sendError()
                    self.__TECincrease()


                    return self.BIT_ERROR
                
            i += 1
            if len(frameBits) == i:
                self.__TECdecrease()
                self.__TECvalues.append([self.__TEC, time.time() - self.__start])
                return self.COMPLITED
            self.__clock.wait()
    
    def __TECincrease(self):
        self.__TEC += 8
        self.__TECvalues.append([self.__TEC, time.time() - self.__start])
        self.errorStatus()

    def __TECdecrease(self):
        if self.__TEC < 1:
            return
        self.__TEC -= 1
        self.__TECvalues.append([self.__TEC, time.time() - self.__start])
        self.errorStatus()

    # def __RECincrease(self):
    #     if not self.checkBound(self.__REC):
    #         return
    #     self.__REC += 8
    #     self.__RECvalues.append([self.__REC, time.time() - self.__start])
    #     self.errorStatus()

    # def __RECdecrease(self):
    #     if not self.checkBound(self.__REC):
    #         return
    #     self.__REC -= 1
    #     self.__RECvalues.append([self.__REC, time.time() - self.__start])
    #     self.errorStatus()

    def errorStatus(self):
        if self.__TEC > 127 or self.__REC > 127:
            self.__status = self.ERROR_PASSIVE
        if self.__TEC <= 127 and self.__REC <= 127:
            self.__status = self.ERROR_ACTIVE
        if self.__TEC > 255:
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

        # if self.__TEC >= 120:
        #     print(f"tec: {self.__TEC} {self.name} flag sended {error_flag}")

        for bit in error_flag:
            self.__canBus.transmitBit(bit)
            self.__clock.wait()
            self.__clock.wait()
            self.__clock.wait()