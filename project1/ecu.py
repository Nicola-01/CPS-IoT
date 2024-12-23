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
    __TECvalues = []
    __RECvalues = []

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
            self.clock.wait()
            self.clock.wait()
            lastSendedBit = self.canBus.getSendedBit()

            print(f"{self.name}; i:{i}; frameBits[i]: {frameBits[i]}; lastSendedBit: {lastSendedBit}\n\n")

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
        elif self.__TEC > 255:
            self.__status = self.BUS_OFF

    def getTEC(self):
        return self.__TEC

    def getStatus(self):
        return self.__status
    
    def diagrams(self):
        """
        Generates diagrams to visualize the evolution of TEC and REC values.
        - The first plot shows the changes in TEC over time.
        - The second plot shows the changes in REC over time.
        """


        # Check if there are any values to plot
        if not self.__TECvalues and not self.__RECvalues:
            print("No data available for diagrams.")
            return

        # Create a figure with two subplots
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # Plot TEC evolution
        if self.__TECvalues:
            axs[0].plot(self.__TECvalues, marker='o', linestyle='-', color='red', label='TEC')
            axs[0].set_title('TEC Evolution Over Time')
            axs[0].set_xlabel('Time Step')
            axs[0].set_ylabel('TEC Value')
            axs[0].grid(True)
            axs[0].legend()

        # Plot REC evolution
        if self.__RECvalues:
            axs[1].plot(self.__RECvalues, marker='o', linestyle='-', color='blue', label='REC')
            axs[1].set_title('REC Evolution Over Time')
            axs[1].set_xlabel('Time Step')
            axs[1].set_ylabel('REC Value')
            axs[1].grid(True)
            axs[1].legend()

        # Adjust layout to avoid overlap
        plt.tight_layout()

        # Display the plots
        plt.show()
