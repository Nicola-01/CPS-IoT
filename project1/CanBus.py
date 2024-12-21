import can
import time
from datetime import datetime
from pathlib import Path
from typing import Literal
import matplotlib.pyplot as plt
import threading

Bit = Literal[0b0, 0b1] 
IDLE = True
ACTIVE = False

ERROR_ACTIVE = 0
ERROR_PASSIVE = 1
BUS_OFF = 2

PERIOD = 2 # seconds

class Frame:
    SOF = 0b0  # Fixed value
    ID = 0b00000000000  # 11-bit identifier for CAN base
    DLC = 0 # Number of bytes of data 
    Data = [0] * 8  # Default: 8 bytes set to 0
    CRC = None
    ACK = 0
    EOF = 0b1111111  # Default CAN EOF

    def __init__(self, ID, dlc, data):
        # # Start of Frame (SOF) is always fixed at 0 in CAN frames
        # self.SOF = 0  
        
        # Identifier (ID): represents the priority of the packet (11-bit for CAN base, 29-bit for CAN extended)
        self.ID = ID  

        self.DLC = dlc  
        
        # Data Field: contains the data (up to 8 bytes of payload)
        self.Data = data  # List of bytes or binary string
        
        # # Cyclic Redundancy Check (CRC): field for verifying data integrity
        # self.CRC = crc  # Normally computed based on the data field
        
        # # Acknowledgment (ACK): indicates whether another node has acknowledged the packet
        # self.ACK = ack  # Default 0: no acknowledgment received
        
        # # End of Frame (EOF): fixed bit sequence indicating the end of the frame
        # self.EOF = 0b111  # For CAN base, EOF consists of 7 recessive bits (111)

    def __str__(self):
        return f"Packet(SOF={self.SOF}, ID={self.ID}, DLC={self.DLC}, Data={self.Data}, CRC={self.CRC}, ACK={self.ACK}, EOF={self.EOF})"

    def getBits(self):
        """Restituisce il frame come una lista di bit concatenati."""
        # Converte SOF in un singolo bit
        sof_bits = [self.SOF]

        # Converte ID (11 bit) in una lista di bit
        id_bits = [int(b) for b in f"{self.ID:011b}"]

        # Converte DLC (4 bit) in una lista di bit
        dlc_bits = [int(b) for b in f"{self.DLC:04b}"]

        # Converte ogni byte di Data in 8 bit ciascuno
        data_bits = []
        for byte in self.Data:
            data_bits.extend([int(b) for b in f"{byte:08b}"])

        # # Converte CRC (se definito) in una lista di bit
        # if self.CRC is not None:
        #     crc_bits = [int(b) for b in f"{self.CRC:015b}"]  # 15-bit CRC
        # else:
        #     crc_bits = []

        # # Converte ACK in un singolo bit
        # ack_bits = [self.ACK]

        # Converte EOF (7 bit) in una lista di bit
        eof_bits = [int(b) for b in f"{self.EOF:07b}"]

        # Combina tutti i bit in una lista
        # return sof_bits + id_bits + dlc_bits + data_bits + crc_bits + ack_bits + eof_bits
        return sof_bits + id_bits + dlc_bits + data_bits + eof_bits

class ECU:

    TEC = 0
    REC = 0
    status = ERROR_ACTIVE

    canBus = None
    frame = None

    TECvalues = []
    RECvalues = []

    def __init__(self, canBus : 'CanBus', frame : Frame):
        self.canBus = canBus
        self.frame = frame

    def sendFrame():
        return None
    
    def errorStatus(self):
        if(self.TEC > 127 or self.REC > 127):
            status = ERROR_PASSIVE
        elif (self.TEC <= 127 and self.REC <= 127):
            status = ERROR_ACTIVE
        elif (self.TEC > 255):
            status = BUS_OFF

    def TECincrease(self):
        self.TEC+=8
        self.TECvalues.append(self.TEC)
        self.errorStatus()

    def RECincrease(self):
        self.REC+=1
        self.RECvalues.append(self.REC)
        self.errorStatus()

    def TECdecrease(self):
        self.TEC-=1
        self.TECvalues.append(self.TEC)
        self.errorStatus()

    def RECdecrease(self):
        self.REC-=1
        self.RECvalues.append(self.REC)
        self.errorStatus()

    def sendFrame(self):
        self.canBus.sendFrame(self.frame)
 
    def checkCanBusFrame(self):
        sendedFrame = self.canBus.getSendedFrame()
        if(sendedFrame != self.frame.getBits):
            self.TECincrease()

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



class CanBus:
    status = IDLE # idle is like trasmiting 1
    signal = 0b1

    frames = []
    lastSendedFrame = None


    def __init__(self):
        ct = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = Path(f"log_{ct}.txt")
        self.file = log_file.open("a")

    def sendFrame(self, frame: 'Frame', ecu: 'ECU'):
        self.frames.append([frame, ecu])
        
        # if bit not in {0b1, 0b0}:
        #     raise ValueError(f"Invalid bit value: {bit}. Only 0b1 and 0b0 are allowed.")

        # self.signal = self.signal & bit
        # time.sleep(0.2)
        # self.signal = 0b1

    def removeInvalidFrames(self):
        """Rimuove i frame con SOF diverso da 0b0."""
        # Filtra solo i frame con SOF uguale a 0b0
        self.frames = [(frame, ecu) for frame, ecu in self.frames if frame.SOF == 0b0]

    def getLowerID(self):
        return min(frame.ID for frame, _ in self.frames)

    def onlyFramesWithID(self, ID):
        self.frames = [(frame, ecu) for frame, ecu in self.frames if frame.ID == ID]
    
    def porcess(self):

        if (self.frames.count == 0):
            pass

        self.removeInvalidFrames()
        lowerID = self.getLowerID()

        self.onlyFramesWithID(lowerID)

        framesBits = [frame.getBits() for frame, _ in self.frames]
        maxLength = max(len(frame) for frame in framesBits)

        frameSended = []

        for i in range(maxLength):
            frameSended.append(1)

            for j in range(framesBits.count):
                if(j<len(framesBits[j])):
                    frameSended[i] = frameSended[i] & framesBits[j][i]

        self.lastSendedFrame = frameSended
    
    def getSendedFrame(self):
        return self.lastSendedFrame

    def clearBus(self):
        self.frames = []
            

def attacker(canBus : 'CanBus', frame : 'Frame'):
    attackerECU = ECU(canBus, frame)

    while attackerECU.getStatus() == ERROR_ACTIVE:
        attackerECU.sendFrame()
        print("attacker sends a frame")
        time.sleep(PERIOD)
        attackerECU.checkCanBusFrame()


def victim(canBus : 'CanBus', frame : 'Frame'):
    victimECU = ECU(canBus, frame)

    while victimECU.getStatus() == ERROR_ACTIVE:
        victimECU.sendFrame()
        print("victim sends a frame")
        time.sleep(PERIOD)
        victimECU.checkCanBusFrame()

def canBusThread(canBus : 'CanBus'):

    while True:
        time.sleep(PERIOD)
        canBus.porcess()
        print("processed frame")
        canBus.clearBus()


if __name__ == "__main__":
    canBus = CanBus()
    attackerFrame = Frame(0b01010101010, 2, [10, 255])
    victimFrame = Frame(0b01010101010, 2, [255, 255])


    canBus_thread = threading.Thread(target=canBusThread(canBus))
    attacker_thread = threading.Thread(target=attacker(canBus, attackerFrame))
    victim_thread = threading.Thread(target=victim(canBus, victimFrame))

    print("threads created")

    canBus_thread.start()
    attacker_thread.start()
    victim_thread.start()
    print("threads started")

    canBus_thread.join()
    attacker_thread.join()
    victim_thread.join()
    print("threads joined")
