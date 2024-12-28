class Frame:

    # https://en.wikipedia.org/wiki/CAN_bus#Base_frame_format

    __SOF = 0b0  # Fixed value
    __ID = 0b00000000000  # 11-bit identifier for CAN base
    __DLC = 0  # Number of bytes of data 
    __Data = [0] * 8  # Default: 8 bytes set to 0
 # __CRC = None  # removed for semplicity
    # __ACK = 0     # removed for semplicity
    __EOF = 0b1111111  # Default CAN EOF

    def __init__(self, ID, dlc, data):
        self.__ID = ID
        self.__DLC = dlc  
        self.__Data = data  # List of bytes or binary string

    def __str__(self):
        return f"Packet(SOF={self.__SOF}, ID={self.__ID}, DLC={self.__DLC}, Data={self.__Data}, EOF={self.__EOF})"
        # return f"Packet(SOF={self.__SOF}, ID={self.__ID}, DLC={self.__DLC}, Data={self.__Data}, CRC={self.__CRC}, ACK={self.__ACK}, EOF={self.__EOF})"
        
    def getID(self):
        return self.__ID    
    
    def getBits(self):
        """Restituisce il frame come una lista di bit concatenati."""
        sof_bits = [self.__SOF]
        id_bits = [int(b) for b in f"{self.__ID:011b}"]
        dlc_bits = [int(b) for b in f"{self.__DLC:04b}"]
        data_bits = []
        for byte in self.__Data:
            data_bits.extend([int(b) for b in f"{byte:08b}"])
        eof_bits = [int(b) for b in f"{self.__EOF:07b}"]

        bitFrame = sof_bits + id_bits + dlc_bits + data_bits + eof_bits

        return self.__addStuffing(bitFrame)
    
    @classmethod
    def fromBits(cls, bits: list):
        """Crea un oggetto Frame a partire da una lista di bit."""
        # Rimuovi i bit di stuffing
        try:
            bits = cls.__removeStuffing(bits)

            # Check della lunghezza minima del frame
            min_length = 1 + 11 + 4 + 7  # SOF + ID + DLC + EOF
            if len(bits) < min_length:
                return None

            # Decodifica i campi
            sof = bits[0]
            ID = int("".join(map(str, bits[1:12])), 2)
            DLC = int("".join(map(str, bits[12:16])), 2)

            # Controllo validità del DLC
            if not (0 <= DLC <= 8):
                return None

            # Decodifica il Data Field
            data_bits = bits[16:16 + (DLC * 8)]
            data = [
                int("".join(map(str, data_bits[i:i + 8])), 2)
                for i in range(0, len(data_bits), 8)
            ]

            # Decodifica l'EOF
            eof_start = 16 + (DLC * 8)
            EOF = int("".join(map(str, bits[eof_start:eof_start + 7])), 2)

            # Controllo EOF
            # if EOF != 0b1111111:
            #     return None

            # Crea e restituisce l'oggetto Frame
            return cls(ID=ID, dlc=DLC, data=data)

        except Exception:
            return None
    
    def __addStuffing(self, bitFrame):
        stuffedFrame = []
        count = 0
        lastBit = None

        for bit in bitFrame:
            stuffedFrame.append(bit)
            if bit == lastBit:
                count += 1
                if count == 5:
                    stuffedFrame.append(1 - bit) # opposit bit
                    count = 0
            else:
                count = 1
            lastBit = bit

        return stuffedFrame
    
    @staticmethod
    def __removeStuffing(bitFrame):
        """Rimuove i bit di stuffing dal frame."""
        unstuffedFrame = []
        count = 0
        lastBit = None

        for i in range(len(bitFrame)):
            if count == 5:
                count = 0
                lastBit = None
                continue
            
            bit = bitFrame[i]
            if bit == lastBit:
                count += 1
            else:
                count = 1
            lastBit = bit
            unstuffedFrame.append(bit)

        return unstuffedFrame
    
    def __eq__(self, other):
        """Confronta due Frame per uguaglianza."""
        if not isinstance(other, Frame):
            return False
        return (
            self.__ID == other.__ID and
            self.__DLC == other.__DLC and
            self.__Data == other.__Data
        )
