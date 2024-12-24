import threading
import matplotlib.pyplot as plt
from ecu import ECU
from can_bus import CanBus
from frame import Frame
from global_clock import GlobalClock

PERIOD = 0.05  # seconds

stop_event = threading.Event()

TECarr = [[], []]
RECarr = [[], []]

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
        canBus.idle_event.wait()
        clock.wait()
        clock.wait()
        '''

def ecuThread(name, index, canBus: 'CanBus', frame: 'Frame'):
    ecu = ECU(name, canBus, frame, clock)
    print(f"{name} frame {frame.getBits()}")
    while not stop_event.is_set() and ecu.getStatus() != ECU.BUS_OFF:
        tranmitedStatus = ecu.sendFrame()
        print(f" tranmitedStatus {tranmitedStatus} \n current {name} TEC {ecu.getTEC()}")
        canBus.idle_event.wait()
        clock.wait()
        clock.wait()

        if ecu.getStatus() == ECU.BUS_OFF:
            stop_event.set()  # Segnala a tutti i thread di fermarsi
            print(f"{name} entered BUS_OFF. Stopping all threads.")
            TECarr[index] = ecu.getTECs()
            RECarr[index] = ecu.getRECs()

def plot_graph(tec_data):

    plt.figure(figsize=(10, 6))

    # Grafico per TEC sovrapposto
    plt.plot(tec_data[0], label='Victim TEC', linestyle='-', marker='o')
    plt.plot(tec_data[1], label='Attacker TEC', linestyle='--', marker='x')
    plt.xlabel('Time')
    plt.ylabel('TEC Value')
    plt.title('TEC Values of Victim and Attacker')
    plt.legend()
    plt.grid(True)

    # Mostra il grafico
    plt.tight_layout()
    plt.show()


def canBusThread(canBus: 'CanBus'):
    # clock.wait()
    while not stop_event.is_set():
        print("canBus")
        clock.wait()
        canBus.nextBit()

        print("-------------------------")
        clock.wait()
        clock.wait()


if __name__ == "__main__":
    clock = GlobalClock(PERIOD)
    clock_thread = threading.Thread(target=clock.start)
    clock_thread.start()

    canBus = CanBus(clock)
    victimFrame = Frame(0b01010101010, 2, [255, 255])
    attackerFrame = Frame(0b01010101010, 2, [64, 64])

    canBus_thread = threading.Thread(target=canBusThread, args=(canBus,))
    ecu_threads = [
        threading.Thread(target=ecuThread, args=("Victim", 0, canBus, victimFrame)),
        threading.Thread(target=ecuThread, args=("Attacker", 1, canBus, attackerFrame))
        ]

    # attacker_thread = threading.Thread(target=attacker, args=(canBus, attackerFrame))

    canBus_thread.start()
    for thread in ecu_threads: thread.start() 

    for thread in ecu_threads:
        thread.join()
    canBus_thread.join()

    print("All threads stopped.")

    plot_graph(TECarr)

    # attacker_thread.start()