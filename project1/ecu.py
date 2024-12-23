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
    FLAG_SENDED = "FLAG_SENDED"

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

            print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n")

            if i >= 1 and i <= 11: # check the id
                if frameBits[i] != lastSendedBit:
                    return self.DIFFERENT_ID # different id, stop transmission

            elif i > 11:
                if frameBits[i] != lastSendedBit:

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

                    self.TECincrease()
                    return self.FLAG_SENDED
                
            i += 1
            if len(frameBits) == i:
                return self.COMPLITED
            self.clock.wait()
    
    def checkBound(self, errorCounter):
        return errorCounter >= 0 and errorCounter <= 255

    def TECincrease(self):
        if not self.checkBound(self.__TEC):
            return
        self.__TEC += 8
        self.__TECvalues.append(self.__TEC)
        self.errorStatus()

    def TECdecrease(self):
        if not self.checkBound(self.__TEC):
            return
        self.__TEC-=1
        self.__TECvalues.append(self.__TEC)
        self.errorStatus()

    def RECincrease(self):
        if not self.checkBound(self.__REC):
            return
        self.__REC+=1
        self.__RECvalues.append(self.__REC)
        self.errorStatus()

    def RECdecrease(self):
        if not self.checkBound(self.__REC):
            return
        self.__REC-=1
        self.__RECvalues.append(self.__REC)
        self.errorStatus()

    def errorStatus(self):
        if self.__TEC > 127 or self.__REC > 127:
            self.__status = self.ERROR_PASSIVE
        elif self.__TEC <= 127 and self.__REC <= 127:
            self.__status = self.ERROR_ACTIVE
        if self.__TEC > 30:
            self.__status = self.BUS_OFF

    def getTEC(self):
        return self.__TEC

    def getStatus(self):
        return self.__status
    
    def getTECarray(self):
        return self.__TEC
    
    def getRECarray(self):
        return self.__TEC
    
    # def diagrams(self):
    #     """
    #     Generates diagrams to visualize the evolution of TEC values.
    #     """
    #     if not self.__TECvalues:
    #         print("No data available for diagrams.")
    #         return

    #     plt.figure(figsize=(10, 6))
    #     plt.plot(self.__TECvalues, marker='o', linestyle='-', color='red', label='TEC Evolution')
    #     plt.title('TEC Evolution Over Time')
    #     plt.xlabel('Time Step')
    #     plt.ylabel('TEC Value')
    #     plt.grid(True)
    #     plt.legend()

    #     # Salva il grafico su file
    #     plt.tight_layout()
    #     filename = f"tec_evolution_{self.name}.png"  # Usa il nome ECU per personalizzare il file
    #     plt.savefig(filename)
    #     print(f"Diagram saved to {filename}")

