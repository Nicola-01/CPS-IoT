import time
import threading

class GlobalClock:
    """
    A class to synchronize processes with periodic signals.
    """
    def __init__(self, period: float, stop_signal: threading.Event):
        """
        Initialize the clock.

        Args:
            period (float): Time in seconds between signals.
            stop_signal (threading.Event): Event to stop the clock thread.
        """
        self.event = threading.Event()  # Synchronization event
        self.period = period  # Clock cycle duration
        self.stop_signal = stop_signal  # Stop signal

    def start(self):
        """
        Run the clock, emitting signals periodically.
        """
        while not self.stop_signal.is_set():
            time.sleep(self.period)  # Wait for the cycle duration
            self.event.set()
            self.event.clear()

    def wait(self):
        """
        Block until the clock emits a signal.
        """
        self.event.wait()  # Wait for signal