import random
import time
import threading
import matplotlib.pyplot as plt

from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

CLOCK = 0.01  # seconds
ECU_NUMBER = 0 # (without count Victim and Adversary)
PERIOD = 5

VICTIM = 0
ADVERSARY = 1

ECUname = ["Victim", "Adversary"]
ECUstopSignal = threading.Event()
CanBusStopSignal = threading.Event()

TECarr = [[], []]

START = time.time()  # Use the current time as the starting point

def attacker(canBus: 'CanBus'):
    frame = None

    victimFrameNumber = None
    victimFrame = None
    period = None

    # time.sleep(2)

    while True:
        clock.wait()
        canBus.waitIdleStatus()
        # print(f" ---- canBus.getCount() {canBus.getCount()};")
        frame = Frame.fromBits(bits=canBus.getSendedFrame())
        if victimFrameNumber != None and victimFrameNumber < canBus.getCount() and victimFrame == frame:
            period = canBus.getCount() - victimFrameNumber
            break

        if victimFrame == None and frame != None:
            victimFrameNumber = canBus.getCount()
            # print(f" ---- victimFrameNumber: {victimFrameNumber};")
            victimFrame = frame
            frame = None
                        
    attackerFrame = Frame(victimFrame.getID(), 1, [0])
                        
    print(f" Adversary found Victim's period: {period}")
    global adversaryStart 
    adversaryStart = True
    ecuThread(ECUname[1], 1, period, canBus, attackerFrame)

start_barrier = threading.Barrier(1 + ECU_NUMBER)
sync_barrier = threading.Barrier(2)

def ecuThread(name, index, period, canBus: 'CanBus', frame: 'Frame'):
    clock.wait()
    ecu = ECU(name, canBus, frame, clock)
    print(f"{name:<11} period: {period:<2} Frame {frame}")
    
    retransmission = False
    lastFrameNumber = 0
    frameTretransmission = 0
    
    global adversaryTransmission 
    global victimTransmission 
    adversaryTransmission = 0
    victimTransmission = 0 
        
    if name != ECUname[ADVERSARY]:
        global adversaryStart 
        adversaryStart = False
        start_barrier.wait()

    while not ECUstopSignal.is_set() and ecu.getStatus() != ECU.BUS_OFF:
        
        # print(f"canBus.getCount() {canBus.getCount()}")
        # print(f"{name:<11}: pre  canBus.getCount() {canBus.getCount()}")
        # while canBus.getCount() % period != 0:
        #     # print(f"while canBus.getCount() {canBus.getCount()}")
        #     # clock.wait()
        #     # clock.wait()
        #     time.sleep(0.001)
        #     # canBus.waitFrameCountIncreese()
            
        if not retransmission: # if retransmission is required, wait for the next period
            # print(f"{name:<11} waitFrameCountMultiple {time.time() - START}")
            franmen = canBus.waitFrameCountMultiple(period)  
            if name == ECUname[VICTIM]:
                victimTransmission = franmen
            elif name == ECUname[ADVERSARY]:
                adversaryTransmission = franmen
            # print(f"{name:<11} exit waitFrameCountMultiple {time.time() - START}")
        else:
            frameTretransmission = lastFrameNumber + 1
            # print(f"{name:<11} retransmission, wait frame {frameTretransmission}")
            canBus.waiFrameCount(frameTretransmission) # wait for the next frame after the
            if name == ECUname[VICTIM]:
                victimTransmission = frameTretransmission
            elif name == ECUname[ADVERSARY]:
                adversaryTransmission = frameTretransmission
            
        retransmission = False
        
        # print(f"{name:<11}: post canBus.getCount() {canBus.getCount()}")
        
        # print(f"{name:<11} wait {time.time() - START}")
            
        clock.wait()
        canBus.waitIdleStatus()
        
        
        # print(f"{name:<11}: adversaryTransmission {adversaryTransmission} victimTransmission {victimTransmission}")
        
        # without this barrier, the adversary can start a cicle before the victim or vice versa
        
        lastFrameNumber = canBus.getCount()
        if (lastFrameNumber == 0 and name != ECUname[VICTIM]):
            continue
        
        if (name in ECUname[:2] and adversaryStart and adversaryTransmission == victimTransmission):
            sync_barrier.wait()
            
        # clock.wait()
        # canBus.waitIdleStatus()
        
        
        # print(f"{name:<11} stop waiting {time.time() - START}")
        # print(f"{name:<11}: Sending frame")
        

        # print(f"{name:<11} start transmission, frameCount {lastFrameNumber}, {time.time() - START}")
        tranmitedStatus = ecu.sendFrame()
        # if tranmitedStatus != ECU.LOWER_FRAME_ID:

        print(f"{name:<11}:tranmitedStatus {tranmitedStatus:<15} TEC {ecu.getTEC():<3} {ecu.getStatus():<13} frameCount {lastFrameNumber}")
        if ecu.getStatus() == ECU.BUS_OFF:
            ECUstopSignal.set()  # Segnala a tutti i thread di fermarsi
            print(f"{name} entered BUS_OFF. Stopping all threads.")
            
        if tranmitedStatus != ECU.COMPLITED:
            canBus.waitIdleStatus()
        # print(f"{name:<11} end transmission {time.time() - START}")

        # retransmition
        if tranmitedStatus == ECU.BIT_ERROR:
            retransmission = True
            continue
        
        canBus.waitIdleStatus()
        # print(f"{name:<11} in idle {time.time() - START}")
        clock.wait() #sync
        clock.wait() #sync
        # canBus.waitFrameCountIncreese()
        # clock.wait()
        # clock.wait()
        # canBus.waitIdleStatus()
            
    TECarr[index] = ecu.getTECs()

def canBusThread(canBus: 'CanBus'):
    while not CanBusStopSignal.is_set():
        clock.wait()

        clock.wait()
        clock.wait()
        
        canBus.nextBit()

def plot_graph(tec_data):
    plt.figure(figsize=(10, 6))

    for i, data in enumerate(tec_data):
        tec = [item[0] for item in data]
        time = [(item[1] - START) * 1000 for item in data]

        plt.plot(time, tec, label=ECUname[i], linestyle='-')

    plt.xlabel('Time (ms)')
    plt.ylabel('TEC Value')
    plt.title('TEC Values over time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    
    random.seed()

    clock = GlobalClock(CLOCK)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus = CanBus(clock)
    victimFrame = Frame(0b01010101010, 2, [255, 255])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_threads = [
        threading.Thread(target=ecuThread, args=(ECUname[0], 0, PERIOD, canBus, victimFrame)),
        threading.Thread(target=attacker, args=(canBus,))
        ]

    for i in range(ECU_NUMBER):
        id = random.randint(0b01010101011, 0b11111111111)
        dlc = random.randint(1, 4) # real valure max ->8 , decreese for increese speed in transmission
        data = []
        for j in range(dlc):
            data.append(random.randint(0, 255))
        
        frame = Frame(id, dlc, data)
        period = random.randint(3, 7)
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
