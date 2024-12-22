import time
import threading
from ecu import ECU
from can_bus import CanBus
from frame import Frame

PERIOD = 0.3  # seconds

class GlobalClock:
    def __init__(self):
        self.event = threading.Event()

    def start(self):
        while True:
            time.sleep(PERIOD)
            self.event.set()  # Segnale per sincronizzare i processi
            self.event.clear()  # Resetta l'evento

    def wait(self):
        self.event.wait()  # Ogni processo aspetta il segnale del clock


def attacker(canBus: 'CanBus', frame: 'Frame'):
    attackerECU = ECU("Attacker", canBus, frame)
    while attackerECU.getStatus() == ECU.BUS_OFF:
        attackerECU.sendFrame()
        print(f"current attacker TEC {attackerECU.getTEC()}")
        clock.wait()
        time.sleep(PERIOD/3)
        attackerECU.checkCanBusFrame()

def victim(canBus: 'CanBus', frame: 'Frame'):
    victimECU = ECU("Victim", canBus, frame)
    while victimECU.getStatus() == ECU.BUS_OFF:
        victimECU.sendFrame()
        print(f"current victim TEC {victimECU.getTEC()}")
        clock.wait()
        time.sleep(PERIOD/3)
        victimECU.checkCanBusFrame()
    victimECU.diagrams()

def canBusThread(canBus: 'CanBus'):
    while True:
        clock.wait()
        # time.sleep(PERIOD/3)
        canBus.process()
        print(f"\n ---------------\nsendendFrame: {canBus.getSendedFrame()}\n ---------------\n")
        canBus.clearBus()



if __name__ == "__main__":
    canBus = CanBus()
    attackerFrame = Frame(0b01010101010, 2, [64, 64])
    victimFrame = Frame(0b01010101010, 2, [255, 255])

    clock = GlobalClock()
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