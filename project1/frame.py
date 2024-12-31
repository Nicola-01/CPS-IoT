class Frame:
    """
    A class representing a CAN bus frame in base format.

    Attributes:
        SOF (int): Start of frame, fixed to 0.
        ID (int): 11 bits identifier for the frame.
        DLC (int): Data Length Code (number of data bytes, 0-8).
        Data (list): List of up to 8 data bytes (default: [0] * 8).
        EOF (int): End of frame, fixed to 0b1111111.
    """

    # https://en.wikipedia.org/wiki/CAN_bus#Base_frame_format
    
    # Constants for the frame structure
    __SOF = 0b0  # Start of Frame, fixed
    __EOF = 0b1111111  # End of Frame, fixed

    # Frame fields
    __ID = 0b00000000000  # 11-bit identifier for CAN base
    __DLC = 0  # Number of bytes of data 
    __Data = [0] * 8  # Default: 8 bytes set to 0
    # __CRC = None  # removed for semplicity
    # __ACK = 0     # removed for semplicity

    def __init__(self, ID: int, dlc: int, data: list):
        """
        Initialize a Frame instance.

        Args:
            ID (int): 11-bit identifier (0-2047).
            dlc (int): Data Length Code (number of data bytes, 0-8).
            data (list): List of data bytes (length must match dlc).
        """
        self.__ID = ID
        self.__DLC = dlc  
        self.__Data = data

    def __str__(self) -> str:
        """Return a string representation of the frame."""
        return f"Frame(SOF={self.__SOF}, ID={self.__ID}, DLC={self.__DLC}, Data={self.__Data}, EOF={self.__EOF})"

    def getID(self) -> int:
        """Get the frame's identifier."""
        return self.__ID    
    
    def getBits(self) -> list:
        """
        Convert the frame into a list of bits, with bit stuffing applied.

        Returns:
            list: The stuffed bit representation of the frame.
        """
        
        # Convert fields to binary and concatenate them
        sof_bits = [self.__SOF]
        id_bits = [int(b) for b in f"{self.__ID:011b}"]
        dlc_bits = [int(b) for b in f"{self.__DLC:04b}"]
        data_bits = [int(bit) for byte in self.__Data for bit in f"{byte:08b}"]
        eof_bits = [int(b) for b in f"{self.__EOF:07b}"]

        # Combine all bit segments and apply stuffing
        bitFrame = sof_bits + id_bits + dlc_bits + data_bits + eof_bits
        return self.__addStuffing(bitFrame)
    
    @classmethod
    def fromBits(cls, bits: list) -> 'Frame':
        """
        Create a Frame instance from a list of bits.

        Args:
            bits (list): List of bits representing a CAN frame.

        Returns:
            Frame: Decoded Frame object, or None if decoding fails.
        """
        
        try:
            # Remove bit stuffing
            bits = cls.__removeStuffing(bits)

            # Minimum frame length: SOF (1) + ID (11) + DLC (4) + EOF (7)
            min_length = 1 + 11 + 4 + 7
            if len(bits) < min_length:
                return None

            # Decode fields from bits
            ID = int("".join(map(str, bits[1:12])), 2)
            DLC = int("".join(map(str, bits[12:16])), 2)

            # Validate DLC
            if not (0 <= DLC <= 8):
                return None

            # Decode Data Field
            data_bits = bits[16:16 + (DLC * 8)]
            data = [
                int("".join(map(str, data_bits[i:i + 8])), 2)
                for i in range(0, len(data_bits), 8)
            ]

            # Decode EOF
            eof_start = 16 + (DLC * 8)
            EOF = int("".join(map(str, bits[eof_start:eof_start + 7])), 2)

            # Validate EOF
            if EOF != 0b1111111:
                return None

            # Create and return the Frame instance
            return cls(ID=ID, dlc=DLC, data=data)

        except Exception:
            return None
    
    def __addStuffing(self, bitFrame: list) -> list:
        """
        Apply bit stuffing to the frame.

        Args:
            bitFrame (list): Original frame bits.

        Returns:
            list: Frame bits with bit stuffing applied.
        """
        
        stuffedFrame = []
        count = 0
        lastBit = None

        for bit in bitFrame:
            stuffedFrame.append(bit)
            if bit == lastBit:
                count += 1
                if count == 5: # 5 consecutive bits of the same value add a bit of the opposite value
                    stuffedFrame.append(1 - bit) # Add opposite bit
                    bit = 1 - bit # Update last bit
                    count = 1 # Reset count, 1 since we added a new bit
            else:
                count = 1
            lastBit = bit

        return stuffedFrame
    
    @staticmethod
    def __removeStuffing(bitFrame: list) -> list:
        """
        Remove bit stuffing from the frame.

        Args:
            bitFrame (list): Frame bits with stuffing.

        Returns:
            list: Frame bits with stuffing removed.
        """
        
        unstuffedFrame = []
        count = 0
        lastBit = None
        
        # The frame is reversed to process the bits from the most recent to the first.
        # This is done to correctly remove stuffing from the end of the sequence.
        # 
        reversed = bitFrame[::-1]

        for bit in reversed:
            if count == 5: # 5 consecutive bits of the same, remove the next bit
                count = 0
                lastBit = None     
                
                # Pop the bit from the list which corresponds to the stuffed bit.
                unstuffedFrame.pop(len(unstuffedFrame) - 1 - 5)
            if bit == lastBit:
                count += 1
            else:
                count = 1
            lastBit = bit
            unstuffedFrame.append(bit)

        # Reverse the frame back to its original
        return unstuffedFrame[::-1]
    
    def __eq__(self, other: object) -> bool:
        """
        Compare two Frame objects for equality.

        Args:
            other (Frame): Another Frame object.

        Returns:
            bool: True if the frames are equal, False otherwise.
        """
        
        if not isinstance(other, Frame):
            return False
        return self.__ID == other.__ID and self.__DLC == other.__DLC and self.__Data == other.__Data