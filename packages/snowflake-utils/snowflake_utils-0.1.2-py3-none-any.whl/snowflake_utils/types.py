from enum import Enum

# Maximun timestamp (0-68719476735)
MAX_TS = 0b11111111111111111111111111111111111111111

# Maximun node id (0-1023)
MAX_NODE_ID = 0b1111111111

# Maximun sequence number (0-4095)
MAX_SEQUENCE = 0b111111111111


class TimestampResolution(Enum):
    """Timestamp resolution enumeration"""

    MILLISECOND = 1
    MICROSECOND = 1000
    # NANOSECOND = 1000000000
