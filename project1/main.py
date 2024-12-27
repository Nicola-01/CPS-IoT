import random
import time
import threading
import matplotlib.pyplot as plt

from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

CLOCK = 0.001  # seconds
ECU_NUMBER = 0 # (without count Victim and Adversary)

ECUname = ["Victim", "Adversary"]
ECUstopSignal = threading.Event()
CanBusStopSignal = threading.Event()

TECarr = [[], []]
# RECarr = [[], []]

# Assuming Start is set at the beginning of the execution
START = time.time()  # Use the current time as the starting point

'''
def attacker(canBus: 'CanBus', frame: 'Frame'):
    attackerECU = ECU("Attacker", canBus, frame, clock)
    print(f"Attacker frame {frame.getBits()}")
    while attackerECU.getStatus() != ECU.BUS_OFF:
        # clock.wait()
        tranmitedStatus = attackerECU.sendFrame()
        print(f" tranmitedStatus {tranmitedStatus} \n current Attacker TEC {attackerECU.getTEC()}")
        # while canBus.getStatus() != canBus.IDLE:
        #     print("Attacker wait")
        #     clock.wait() 
        canBus.idleEvent.wait()
        clock.wait()
        clock.wait()
        '''

def ecuThread(name, index, period, canBus: 'CanBus', frame: 'Frame'):
    ecu = ECU(name, canBus, frame, clock, START)
    print(f"{name} frame {frame.getBits()}")

    count = 0
    while not ECUstopSignal.is_set() and ecu.getStatus() != ECU.BUS_OFF:

        if count == period:
            tranmitedStatus = ecu.sendFrame()
            if tranmitedStatus != ECU.LOWER_FRAME_ID:
                print(f"{name}: tranmitedStatus {tranmitedStatus}; TEC {ecu.getTEC()}")
            count = -1
        else:
            clock.wait()
        count += 1 

        canBus.idleEvent.wait()
        clock.wait() #sync
        clock.wait()

        if ecu.getStatus() == ECU.BUS_OFF:
            ECUstopSignal.set()  # Segnala a tutti i thread di fermarsi
            print(f"{name} entered BUS_OFF. Stopping all threads.")

    TECarr[index] = ecu.getTECs()

def plot_graph(tec_data):
    # Check if the input data is in the correct format
    # if len(tec_data) != 2 or len(tec_data[0]) == 0 or len(tec_data[1]) == 0:
    #     print("Error: TEC data is not in the correct format or empty.")
    #     return

    # Extract time and TEC values for Victim and Attacker
    # victim_tec = [item[0] for item in tec_data[0]]
    # victim_time = [item[1] * 1000 for item in tec_data[0]]  # Convert seconds to milliseconds

    # attacker_tec = [item[0] for item in tec_data[1]]
    # attacker_time = [item[1] * 1000 for item in tec_data[1]]  # Convert seconds to milliseconds

    plt.figure(figsize=(10, 6))

    for i, data in enumerate(tec_data):
        tec = [item[0] for item in data]
        time = [item[1] * 1000 for item in data]

        plt.plot(time, tec, label=ECUname[i], linestyle='-')

    
    # plt.figure(figsize=(10, 6))

    # plt.plot(victim_time, victim_tec, label='Victim\'s TEC', linestyle='-')
    # # Plot TEC values for both Victim and Attacker
    # plt.plot(attacker_time, attacker_tec, label='Adversary\'s TEC', linestyle='-.')

    # Add labels and title
    plt.xlabel('Time (ms)')
    plt.ylabel('TEC Value')
    plt.title('TEC Values over time')

    # Show legend
    plt.legend()

    # Add grid for better visualization
    plt.grid(True)

    # Show the plot with tight layout
    plt.tight_layout()

    # Print the TEC data for debugging
    # print("TEC Data:", tec_data)

    # Display the graph
    plt.show()

def canBusThread(canBus: 'CanBus'):
    # clock.wait()
    while not CanBusStopSignal.is_set():
        # print("canBus")
        clock.wait()
        canBus.nextBit()

        # print("-------------------------")
        clock.wait()
        clock.wait()


if __name__ == "__main__":
    
    random.seed()

    clock = GlobalClock(CLOCK)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus = CanBus(clock)
    victimFrame = Frame(0b01010101010, 2, [255, 255])
    attackerFrame = Frame(0b01010101010, 2, [64, 64])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_threads = [
        threading.Thread(target=ecuThread, args=(ECUname[0], 0, 5, canBus, victimFrame)),
        threading.Thread(target=ecuThread, args=(ECUname[1], 1, 5, canBus, attackerFrame))
        ]

    for i in range(ECU_NUMBER):
        id = random.randint(0b01010101011, 0b11111111111)
        dlc = random.randint(1, 4) # real valure max ->8 , decreese for increese speed in transmission
        data = []
        for j in range(dlc):
            data.append(random.randint(0, 255))
        
        frame = Frame(id, dlc, data)
        period = random.randint(5, 10)
        ECUname.append(f"ECU{i+1}")
        TECarr.append([])

        ecu_threads.append(threading.Thread(target=ecuThread, args=(ECUname[-1], i+2, period, canBus, frame)))

    # attacker_thread = threading.Thread(target=attacker, args=(canBus, attackerFrame))

    canBus_thread.start()
    for thread in ecu_threads: thread.start() 

    for thread in ecu_threads: thread.join()

    CanBusStopSignal.set() # wait all threads to stop canbus 

    print("All threads stopped.")

    plot_graph(TECarr)

    # attacker_thread.start()
