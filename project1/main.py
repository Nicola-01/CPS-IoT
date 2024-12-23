import threading
from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

PERIOD = 0.1  # seconds

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
        canBus.idle_event.wait()
        clock.wait()
        clock.wait()

def ecuThread(name, canBus: 'CanBus', frame: 'Frame'):
    ecu = ECU(name, canBus, frame, clock)
    print(f"{name} frame {frame.getBits()}")
    while ecu.getStatus() != ECU.BUS_OFF:
        tranmitedStatus = ecu.sendFrame()
        print(f" tranmitedStatus {tranmitedStatus} \n current {name} TEC {ecu.getTEC()}")
        canBus.idle_event.wait()
        clock.wait()
        clock.wait()


def canBusThread(canBus: 'CanBus'):
    # clock.wait()
    while True:
        print("canBus")
        clock.wait()
        canBus.nextBit()

        print("-------------------------")
        clock.wait()
        clock.wait()
        # if canBus.getStatus() == canBus.IDLE:
        #     print(f"\n clearBus ---------------\nsendendFrame: {canBus.getSendedFrame()}\n ---------------\n")
        #     # canBus.clearBus()
        #     clock.wait()
        # canBus.idle_event.wait()



if __name__ == "__main__":
    clock = GlobalClock(PERIOD)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus = CanBus(clock)
    victimFrame = Frame(0b01010101010, 2, [255, 255])
    attackerFrame = Frame(0b01010101010, 2, [64, 64])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_thread = [
        threading.Thread(target=ecuThread, args=("Victim", canBus, victimFrame)),
        threading.Thread(target=ecuThread, args=("Attacker", canBus, attackerFrame))
        ]

    # attacker_thread = threading.Thread(target=attacker, args=(canBus, attackerFrame))

    canBus_thread.start()
    for thread in ecu_thread: thread.start() 

    # attacker_thread.start()