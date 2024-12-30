import random
import time
import threading
import matplotlib.pyplot as plt

from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

# Customisable Parameters
CLOCK = 0.005  # Time step in seconds
ECU_NUMBER = 0  # Number of additional ECUs (excluding Victim and Adversary)
                # Not proprerty used in this implementation, but can be used to add more ECUs, 
                # but this can create some issues with the synchronization
PERIOD = 5  # Transmission period for Victim and Adversary ECU
            # must be at least 5 to ensure proper synchronization.

# Fixed Parameters (these should not be modified)
ECUname = ["Victim", "Adversary"]
VICTIM = 0  # Index for the Victim ECU
ADVERSARY = 1  # Index for the Adversary ECU

ECUstopSignal = threading.Event()  # Event to stop all ECU threads
CanBusStopSignal = threading.Event()  # Event to stop the CAN Bus thread
GlobalClockStopSignal = threading.Event()  # Event to stop the Global clock thread

# I tried to avoid using barriers for synchronization, as it's possible to synchronize the threads without them (was my first implementation). 
# However, there were some issues with thread synchronization where one of the threads lost sync, causing 
# transmissions to happen in different CAN bus cycles. As a result, these barriers are now used to ensure proper synchronization.
start_barrier = threading.Barrier(1 + ECU_NUMBER)  # Barrier to synchronize ECU threads at start
sync_barrier = threading.Barrier(2)  # Barrier for synchronizing the transmission of victim and adversary

TECarr = [[], []] # List to store TEC data for each ECU

START = time.time()  # Starting time for the simulation (used for time calculations)

def attacker(canBus: 'CanBus'):
    """
    Simulates the attacker ECU. It monitors the frames on the CAN bus and tries to find the 
    Victim's transmission period by detecting the periodic transmission of the Victim's ID.
    Once the period is detected, the attacker ECU begins its own transmission to do a Bus-off attack.
    """
    
    frame = None
    victimFrameNumber = None
    victimFrame = None
    period = None

    # Wait for a frame to match the Victim's periodic transmission
    while True:
        clock.wait()   # Synchronize with the global clock
        canBus.waitIdleStatus()  # Ensure the CAN bus is idle
        frame = Frame.fromBits(bits=canBus.getSendedFrame()) # Get the frame from the bus
        
        if victimFrameNumber != None and victimFrameNumber < canBus.getCount() and victimFrame == frame:
            period = canBus.getCount() - victimFrameNumber # Calculate the transmission period
            break

        if victimFrame == None and frame != None:
            victimFrameNumber = canBus.getCount()
            victimFrame = frame
            frame = None
                        
    # Create an attacker frame using the same ID as the Victim's frame
    attackerFrame = Frame(victimFrame.getID(), 0, [])
                        
    print(f"Adversary found Victim's period: {period}")
    global adversaryStart 
    adversaryStart = True
    ecuThread(ECUname[1], 1, period, canBus, attackerFrame)  # Start the adversary ECU thread


def ecuThread(name, index: int, period: int, canBus: 'CanBus', frame: 'Frame'):
    """
    Represents the ECU thread that handles transmission and retransmission of frames on the CAN bus.
    Each ECU waits for its turn to transmit based on its period, or retransmits if there is an error.
    """
    
    clock.wait()  # Synchronize with the global clock
    ecu = ECU(name, canBus, clock)  # Create the ECU instance
    print(f"Start {name:<9} -> Period: {period:<2}; {frame}")
    
    retransmission = False
    lastFrameNumber = 0
    frameTretransmission = 0
    
    # Declare the variables as global to share them across different functions/threads
    global adversaryTransmission 
    global victimTransmission 
    
    # Initialize the transmission counters for both the adversary and the victim
    # These counters track the number of transmissions each ECU has made
    # Used for synchronization between the victim and adversary
    adversaryTransmission = 0
    victimTransmission = 0 
        
    if name != ECUname[ADVERSARY]:
        global adversaryStart 
        adversaryStart = False
        start_barrier.wait()  # Wait for all ECUs to start

    # ECU threads stop when one ECU enters the BUS_OFF state
    while not ECUstopSignal.is_set() and ecu.getStatus() != ECU.BUS_OFF:

        if retransmission:  # retransmit in case of an error without waiting for the period
            frameTretransmission = lastFrameNumber + 1
            canBus.waitFrameCount(frameTretransmission) # wait for the next frame for start the retransmission
            
            # update the transmission counters
            if name == ECUname[VICTIM]:
                victimTransmission = frameTretransmission
            elif name == ECUname[ADVERSARY]:
                adversaryTransmission = frameTretransmission
                
        else: # Wait the next period to transmit a frame 
            franmen = canBus.waitFrameCountMultiple(period)  
            
            # update the transmission counters
            if name == ECUname[VICTIM]:
                victimTransmission = franmen
            elif name == ECUname[ADVERSARY]:
                adversaryTransmission = franmen
            
        retransmission = False  # Reset retransmission flag
        
        # Sync
        clock.wait()
        canBus.waitIdleStatus()
        
        lastFrameNumber = canBus.getCount()  # Get the current frame count   
        
        # Synchronize victim and adversary transmission cycles   
        if (name in ECUname[:2] and adversaryStart and adversaryTransmission == victimTransmission):
            sync_barrier.wait()
            
        transmitedStatus = ecu.sendFrame(frame) # Send the frame on the bus and get the transmission status
        print(f"   {name:<9} | ECU: TEC: {ecu.getTEC():<3}, Status: {ecu.getStatus():<13} | Transmitted frame status: {transmitedStatus:<9} | CanBus slot: {lastFrameNumber}")

        
        # Check if the ECU has entered BUS_OFF state
        if ecu.getStatus() == ECU.BUS_OFF:
            ECUstopSignal.set()  # Stop all threads if BUS_OFF state is reached
            print(f"{name} entered BUS_OFF. Stopping all threads.")

        # Retransmission if a bit error occurs
        if transmitedStatus != ECU.COMPLITED:
            retransmission = True
            continue
        
        # Sync
        canBus.waitIdleStatus()
        clock.wait() 
        clock.wait()
            
    TECarr[index] = ecu.getTECs()  # Store TEC data for later plotting

def canBusThread(canBus: 'CanBus'):
    """
    Simulates the CAN bus operation.
    """
    while not CanBusStopSignal.is_set():
        clock.wait()
        clock.wait()
        clock.wait()
        canBus.process() # Save the current bit in the frame and wait for the next bit or the end of the frame

def plot_graph(tec_data):
    """
    Plots the TEC (Transmitter Error Counter) values over time for each ECU.
    """
    
    plt.figure(figsize=(10, 6))

    # Plot the TEC values for each ECU
    for i, data in enumerate(tec_data):
        tec = [item[0] for item in data]
        time = [(item[1] - START) * 1000 for item in data]

        plt.plot(time, tec, label=ECUname[i]+"'s TEC", linestyle='-')

    plt.xlabel('Time [ms]')
    plt.ylabel('TEC Value')
    plt.title('TEC Values over time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()
        
def randomFrame() -> 'Frame':
    """
    Generates a random frame with a random ID, DLC, and data.
    """
    
    id = random.randint(0b00000000000, 0b11111111111)
    dlc = random.randint(1, 4)  # Data Length Code (DLC) between 1 and 4 bytes
                                # The real DLC can be between 0 and 8 bytes, but for speed, I limit it to 4 bytes
    data = []
    for i in range(dlc):
        data.append(random.randint(0, 255))
    
    return Frame(id, dlc, data)

if __name__ == "__main__":
    """
    Main function to initialize and start the simulation.
    """
    
    random.seed()  # Initialize random seed

    # Create a global clock and start its thread
    clock = GlobalClock(CLOCK, GlobalClockStopSignal)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    # Initialize the CAN bus
    canBus = CanBus(clock)
    
    victimFrame = randomFrame()  # Generate a random frame for the Victim ECU

    # Generate the threads for the canBus, victim, and attacker
    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_threads = [
        threading.Thread(target=ecuThread, args=(ECUname[0], 0, PERIOD, canBus, victimFrame)),
        threading.Thread(target=attacker, args=(canBus,))
        ]

    # Create additional ECUs
    for i in range(ECU_NUMBER):
        frame = randomFrame()
        period = random.randint(PERIOD, PERIOD * 3)  # Random period for the ECU
        ECUname.append(f"ECU{i+1}")
        TECarr.append([])

        ecu_threads.append(threading.Thread(target=ecuThread, args=(ECUname[-1], i+2, period, canBus, frame)))

    # Start all threads
    canBus_thread.start()
    for thread in ecu_threads: thread.start() 

    # Wait for all ECU threads to finish
    for thread in ecu_threads: thread.join()

    # Wait all ECU threads to stop canbus thread 
    CanBusStopSignal.set()
    
    # Stop the GlobalClock thread
    GlobalClockStopSignal.set()

    print("All threads stopped.")
    
    # Plot the TEC graph for all ECUs   
    plot_graph(TECarr)