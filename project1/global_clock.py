import time
import threading

class GlobalClock:
    """
    A class to synchronize processes with periodic signals.
    """
    def __init__(self, period):
        """
        Initialize the clock.

        Args:
            period (float): Time in seconds between signals.
        """
        self.event = threading.Event()  # Synchronization event
        self.period = period  # Clock cycle duration

    def start(self):
        """
        Run the clock, emitting signals periodically.
        """
        while True:
            time.sleep(self.period)  # Wait for the cycle duration
            self.event.set()
            self.event.clear()

    def wait(self):
        """
        Block until the clock emits a signal.
        """
        self.event.wait()  # Wait for signal