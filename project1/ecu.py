from frame import Frame
from can_bus import CanBus
import matplotlib.pyplot as plt

class ECU:
    ERROR_ACTIVE = 0
    ERROR_PASSIVE = 1
    BUS_OFF = 2

    ERROR_ACTIVE_FLAG = 0b000000
    ERROR_PASSIVE_FLAG = 0b111111

    TEC = 0
    REC = 0
    status = ERROR_ACTIVE
    TECvalues = []
    RECvalues = []

    def __init__(self, name, canBus: 'CanBus', frame: 'Frame'):
        self.name = name
        self.canBus = canBus
        self.frame = frame

    def sendFrame(self):
        self.canBus.sendFrameOnBus(self.frame)

    def checkCanBusFrame(self):
        canBusFrame = self.canBus.getSendedFrame()
        ecuFrameBits = self.frame.getBits()
        if canBusFrame[1:12] == canBusFrame[1:12]: # check if is the same ID
            if canBusFrame != ecuFrameBits: # than check the msg
                # TODO: send error flag
                self.TECincrease()
                # print(f"Mismatch detected {self.name}:\nCAN Bus Frame: {canBusFrame}\nECU Frame Bits: {ecuFrameBits}")
            else:
                self.TECdecrease()
    
    def checkBound(self, errorCounter):
        return errorCounter >= 0 and errorCounter <= 255

    def TECincrease(self):
        if self.checkBound(self.TEC):
            return
        self.TEC += 8
        self.TECvalues.append(self.TEC)
        self.errorStatus()

    def TECdecrease(self):
        if self.checkBound(self.TEC):
            return
        self.TEC-=1
        self.TECvalues.append(self.TEC)
        self.errorStatus()

    def RECincrease(self):
        if self.checkBound(self.REC):
            return
        self.REC+=1
        self.RECvalues.append(self.REC)
        self.errorStatus()

    def RECdecrease(self):
        if self.checkBound(self.REC):
            return
        self.REC-=1
        self.RECvalues.append(self.REC)
        self.errorStatus()

    def errorStatus(self):
        if self.TEC > 127 or self.REC > 127:
            self.status = self.ERROR_PASSIVE
        elif self.TEC <= 127 and self.REC <= 127:
            self.status = self.ERROR_ACTIVE
        elif self.TEC > 255:
            self.status = self.BUS_OFF

    def getTEC(self):
        return self.TEC

    def getStatus(self):
        return self.status
    
    def diagrams(self):
        """
        Generates diagrams to visualize the evolution of TEC and REC values.
        - The first plot shows the changes in TEC over time.
        - The second plot shows the changes in REC over time.
        """


        # Check if there are any values to plot
        if not self.TECvalues and not self.RECvalues:
            print("No data available for diagrams.")
            return

        # Create a figure with two subplots
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # Plot TEC evolution
        if self.TECvalues:
            axs[0].plot(self.TECvalues, marker='o', linestyle='-', color='red', label='TEC')
            axs[0].set_title('TEC Evolution Over Time')
            axs[0].set_xlabel('Time Step')
            axs[0].set_ylabel('TEC Value')
            axs[0].grid(True)
            axs[0].legend()

        # Plot REC evolution
        if self.RECvalues:
            axs[1].plot(self.RECvalues, marker='o', linestyle='-', color='blue', label='REC')
            axs[1].set_title('REC Evolution Over Time')
            axs[1].set_xlabel('Time Step')
            axs[1].set_ylabel('REC Value')
            axs[1].grid(True)
            axs[1].legend()

        # Adjust layout to avoid overlap
        plt.tight_layout()

        # Display the plots
        plt.show()
