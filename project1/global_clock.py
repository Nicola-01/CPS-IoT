import time
import threading

class GlobalClock:
    def __init__(self, period):
        self.event = threading.Event()
        self.period = period

    def start(self):
        while True:
            time.sleep(self.period)
            self.event.set()  # Segnale per sincronizzare i processi
            self.event.clear()  # Resetta l'evento
            print("---clock---\n")

    def wait(self):
        self.event.wait()  # Ogni processo aspetta il segnale del clock