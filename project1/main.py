import random
import time
import threading
import matplotlib.pyplot as plt

from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

CLOCK = 0.005  # seconds
CLOCK = 0.5  # seconds
ECU_NUMBER = 0 # (without count Victim and Adversary)

ECUname = ["Victim", "Adversary"]
ECUstopSignal = threading.Event()
CanBusStopSignal = threading.Event()

TECarr = [[], []]

START = time.time()  # Use the current time as the starting point

def attacker(canBus: 'CanBus'):
    frame = None

    victimFrameNumber = 10**100
    victimFrame = None
    firstTransmition = None
    transmitionTime = None

    time.sleep(2)

    while True:
        frame = Frame.fromBits(bits=canBus.getSendedFrame())
        if victimFrameNumber < canBus.getCount() and victimFrame == frame:
            transmitionTime = time.time() - firstTransmition
            print(f" ---- time: {transmitionTime};")
            break

        if victimFrame == None and frame != None:
            victimFrameNumber = canBus.getCount()
            victimFrame = frame
            frame = None
            firstTransmition = time.time()


    

def ecuThread(name, index, period, canBus: 'CanBus', frame: 'Frame'):
    ecu = ECU(name, canBus, frame, clock, START)
    print(f"{name:<11} period: {period:<5} \tFrame {frame}")

    startTime = time.time()

    previusSend = None

    while not ECUstopSignal.is_set() and ecu.getStatus() != ECU.BUS_OFF:

        while canBus.idleEvent.is_set() and abs(((time.time() - startTime)) % (period)) > period/10: # 10% of period
            pass

        clock.wait() #sync
        clock.wait()
        
        if previusSend == None:
            previusSend = time.time()
        else:
            send = time.time()
            print(f"time to send {send-previusSend}")
            previusSend = send

        tranmitedStatus = ecu.sendFrame()
        # if tranmitedStatus != ECU.LOWER_FRAME_ID:
        print(f"{name:<11}:\ttranmitedStatus {tranmitedStatus:<15} TEC {ecu.getTEC():<3} {ecu.getStatus()}")

        if ecu.getStatus() == ECU.BUS_OFF:
            ECUstopSignal.set()  # Segnala a tutti i thread di fermarsi
            print(f"{name} entered BUS_OFF. Stopping all threads.")

        # todo retransmition

        # canBus.idleEvent.wait()


    TECarr[index] = ecu.getTECs()

def plot_graph(tec_data):
    plt.figure(figsize=(10, 6))

    for i, data in enumerate(tec_data):
        tec = [item[0] for item in data]
        time = [item[1] * 1000 for item in data]

        plt.plot(time, tec, label=ECUname[i], linestyle='-')

    plt.xlabel('Time (ms)')
    plt.ylabel('TEC Value')
    plt.title('TEC Values over time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()

def canBusThread(canBus: 'CanBus'):
    while not CanBusStopSignal.is_set():
        clock.wait()
        canBus.nextBit()

        clock.wait()
        clock.wait()
        print("canBus cicle, status: ", canBus.getStatus())


if __name__ == "__main__":
    
    random.seed()

    clock = GlobalClock(CLOCK)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus = CanBus(clock)
    victimFrame = Frame(0b01010101010, 2, [128, 13])
    attackerFrame = Frame(0b01010101010, 2, [64, 64])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_threads = [
        threading.Thread(target=ecuThread, args=(ECUname[0], 0, CLOCK * 100 * 1, canBus, victimFrame)),
        threading.Thread(target=attacker, args=(canBus,))
        # threading.Thread(target=ecuThread, args=(ECUname[0], 0, CLOCK * 5, canBus, attackerFrame))
        ]

    for i in range(ECU_NUMBER):
        id = random.randint(0b01010101011, 0b11111111111)
        dlc = random.randint(1, 4) # real valure max ->8 , decreese for increese speed in transmission
        data = []
        for j in range(dlc):
            data.append(random.randint(0, 255))
        
        frame = Frame(id, dlc, data)
        period = CLOCK * random.randint(8, 12)
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
