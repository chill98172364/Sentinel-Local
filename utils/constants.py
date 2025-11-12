from enum import Enum, unique
from enum import IntEnum, unique

@unique
class AdvisorySource(Enum):
    """Maps various security advisory sources for categorizing"""
    NVD = "NVD"
    DSA = "DSA"
    USA = "USA"
    DARK_READING = "darkReading"
    HACKER_NEWS = "hackerNews"
    KERBON_SECURITY = "kerbonSecurity"
    MSRC = "MSRC"
    RED_HAT = "redHat"

@unique
class TimeUnits(IntEnum):
    minute = 60
    hour = 3600
    day = 86400