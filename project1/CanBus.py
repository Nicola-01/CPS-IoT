import can
import time

def attacker():
    """Attacker sending corrupted messages to induce errors"""
    with can.Bus(interface='virtual', channel='vcan0', bitrate=250000) as bus:
        # Pacchetto con dati corrotti per cercare di generare errori
        corrupted_msg = can.Message(arbitration_id=0x123, data=[0xFF, 0xFF, 0xFF, 0xFF], is_extended_id=False)
        
        # Invio continuo di messaggi corrotti per sovraccaricare la vittima
        while True:
            bus.send(corrupted_msg)
            print(f"Attacker sent corrupted message: {corrupted_msg}")
            time.sleep(0.1)  # pausa tra i messaggi

def victim():
    """Simulates a victim receiving messages and reacting to errors"""
    with can.Bus(interface='virtual', channel='vcan0', bitrate=250000) as bus:
        try:
            while True:
                message = bus.recv()  # riceve i messaggi dal bus
                if message is not None:
                    print(f"Victim received message: {message}")
        except can.CanError as e:
            print(f"Victim encountered error: {e}")

if __name__ == "__main__":
    import threading
    # Avvia l'attaccante e la vittima in thread separati
    attacker_thread = threading.Thread(target=attacker)
    victim_thread = threading.Thread(target=victim)

    attacker_thread.start()
    victim_thread.start()

    attacker_thread.join()
    victim_thread.join()
