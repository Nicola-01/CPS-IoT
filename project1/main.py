import time
import threading
from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

PERIOD = 0.1  # seconds

def attacker(canBus: 'CanBus', frame: 'Frame'):
    attackerECU = ECU("Attacker", canBus, frame)
    print(f"Attacker frame {frame.getBits()}")
    while attackerECU.getStatus() != ECU.BUS_OFF:
        tranmitedStatus = attackerECU.sendFrame(clock)
        # print(f"\n tranmitedStatus {tranmitedStatus} \n current Attacker TEC {attackerECU.getTEC()}")
        while canBus.getStatus() != canBus.IDLE:
            print("Attacker wait")
            clock.wait() 


def victim(canBus: 'CanBus', frame: 'Frame'):
    victimECU = ECU("Victim", canBus, frame)
    print(f"Victim frame   {frame.getBits()}")
    while victimECU.getStatus() != ECU.BUS_OFF:
        tranmitedStatus = victimECU.sendFrame(clock)
        # print(f"\n tranmitedStatus {tranmitedStatus} \n current Victim TEC {victimECU.getTEC()}")
        while canBus.getStatus() != canBus.IDLE:
            print("Victim wait")
            clock.wait() 

def canBusThread(canBus: 'CanBus'):
    while True:
        clock.wait()
        canBus.nextBit()
        clock.wait()
        clock.wait()
        if canBus.getStatus() == canBus.IDLE:
            print(f"\n ---------------\nsendendFrame: {canBus.getSendedFrame()}\n ---------------\n")
            canBus.clearBus()



if __name__ == "__main__":
    canBus = CanBus()
    attackerFrame = Frame(0b01010101010, 2, [64, 64])
    victimFrame = Frame(0b01010101010, 2, [255, 255])

    clock = GlobalClock(PERIOD)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    attacker_thread = threading.Thread(target=attacker, args=(canBus, attackerFrame))
    victim_thread = threading.Thread(target=victim, args=(canBus, victimFrame))

    canBus_thread.start()
    attacker_thread.start()
    victim_thread.start()

    canBus_thread.join()
    attacker_thread.join()
    victim_thread.join()