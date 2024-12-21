import time
import threading
from ecu import ECU
from can_bus import CanBus
from frame import Frame

PERIOD = 10  # seconds

def attacker(canBus: 'CanBus', frame: 'Frame'):
    attackerECU = ECU("Attacker", canBus, frame)
    while attackerECU.getStatus() == ECU.ERROR_ACTIVE:
        attackerECU.sendFrame()
        print(f"current attacker TEC {attackerECU.getTEC()}")
        time.sleep(PERIOD)
        attackerECU.checkCanBusFrame()

def victim(canBus: 'CanBus', frame: 'Frame'):
    victimECU = ECU("Victim", canBus, frame)
    while victimECU.getStatus() == ECU.ERROR_ACTIVE:
        victimECU.sendFrame()
        print(f"current victim TEC {victimECU.getTEC()}")
        time.sleep(PERIOD)
        victimECU.checkCanBusFrame()

def canBusThread(canBus: 'CanBus'):
    while True:
        time.sleep(PERIOD)
        canBus.process()
        print(f"\n ---------------\nsendendFrame: {canBus.getSendedFrame()}\n ---------------\n")
        canBus.clearBus()



if __name__ == "__main__":
    canBus = CanBus()
    attackerFrame = Frame(0b01010101010, 2, [64, 64])
    victimFrame = Frame(0b01010101010, 2, [255, 255])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    attacker_thread = threading.Thread(target=attacker, args=(canBus, attackerFrame))
    victim_thread = threading.Thread(target=victim, args=(canBus, victimFrame))

    canBus_thread.start()
    attacker_thread.start()
    victim_thread.start()

    canBus_thread.join()
    attacker_thread.join()
    victim_thread.join()