class Frame:
    SOF = 0b0  # Fixed value
    ID = 0b00000000000  # 11-bit identifier for CAN base
    DLC = 0  # Number of bytes of data 
    Data = [0] * 8  # Default: 8 bytes set to 0
    CRC = None
    ACK = 0
    EOF = 0b1111111  # Default CAN EOF

    def __init__(self, ID, dlc, data):
        self.ID = ID
        self.DLC = dlc  
        self.Data = data  # List of bytes or binary string

    def __str__(self):
        return f"Packet(SOF={self.SOF}, ID={self.ID}, DLC={self.DLC}, Data={self.Data}, CRC={self.CRC}, ACK={self.ACK}, EOF={self.EOF})"

    def getBits(self):
        """Restituisce il frame come una lista di bit concatenati."""
        sof_bits = [self.SOF]
        id_bits = [int(b) for b in f"{self.ID:011b}"]
        dlc_bits = [int(b) for b in f"{self.DLC:04b}"]
        data_bits = []
        for byte in self.Data:
            data_bits.extend([int(b) for b in f"{byte:08b}"])
        eof_bits = [int(b) for b in f"{self.EOF:07b}"]

        return sof_bits + id_bits + dlc_bits + data_bits + eof_bits
