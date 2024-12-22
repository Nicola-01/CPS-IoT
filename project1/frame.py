class Frame:
    __SOF = 0b0  # Fixed value
    __ID = 0b00000000000  # 11-bit identifier for CAN base
    __DLC = 0  # Number of bytes of data 
    __Data = [0] * 8  # Default: 8 bytes set to 0
    __CRC = None
    __ACK = 0
    __EOF = 0b1111111  # Default CAN EOF

    def __init__(self, ID, dlc, data):
        self.__ID = ID
        self.__DLC = dlc  
        self.__Data = data  # List of bytes or binary string

    def __str__(self):
        return f"Packet(SOF={self.__SOF}, ID={self.__ID}, DLC={self.__DLC}, Data={self.__Data}, CRC={self.__CRC}, ACK={self.__ACK}, EOF={self.__EOF})"

    def getBits(self):
        """Restituisce il frame come una lista di bit concatenati."""
        sof_bits = [self.__SOF]
        id_bits = [int(b) for b in f"{self.__ID:011b}"]
        dlc_bits = [int(b) for b in f"{self.__DLC:04b}"]
        data_bits = []
        for byte in self.__Data:
            data_bits.extend([int(b) for b in f"{byte:08b}"])
        eof_bits = [int(b) for b in f"{self.__EOF:07b}"]

        return sof_bits + id_bits + dlc_bits + data_bits + eof_bits
