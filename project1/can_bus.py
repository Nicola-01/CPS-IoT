import threading
from frame import Frame

class CanBus:
    def __init__(self):
        self.frames = []
        self.lastSendedFrame = None
        self.lock = threading.Lock()

    def sendFrameOnBus(self, frame: 'Frame'):
        with self.lock:
            self.frames.append(frame)

    def process(self):
        with self.lock:
            if len(self.frames) == 0:
                return

            self.removeInvalidFrames()
            lowerID = self.getLowerID()
            self.onlyFramesWithID(lowerID)

            framesBits = [frame.getBits() for frame in self.frames]
            maxLength = max(len(frame) for frame in framesBits)

            frameSended = []

            for i in range(maxLength):
                frameSended.append(1)  # Default recessive bit

                for j in range(len(framesBits)):
                    if j < len(framesBits[j]):
                        frameSended[i] &= framesBits[j][i]  # Dominant bits win

            print(f"Processed frame bits: {frameSended}")
            self.lastSendedFrame = frameSended

    def getSendedFrame(self):
        return self.lastSendedFrame

    def clearBus(self):
        self.frames = []

    def removeInvalidFrames(self):
        """Rimuove i frame con SOF diverso da 0b0."""
        self.frames = [frame for frame in self.frames if frame.SOF == 0b0]

    def getLowerID(self):
        return min(frame.ID for frame in self.frames)

    def onlyFramesWithID(self, ID):
        self.frames = [frame for frame in self.frames if frame.ID == ID]
