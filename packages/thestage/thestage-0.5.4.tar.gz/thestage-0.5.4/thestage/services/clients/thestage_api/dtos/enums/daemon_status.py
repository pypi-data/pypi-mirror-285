from enum import Enum
from typing import List


class DaemonStatusEnumDto(str, Enum):
    NEW: str = 'NEW'
    ONLINE: str = 'ONLINE'
    OFFLINE: str = 'OFFLINE'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['DaemonStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == DaemonStatusEnumDto.ALL else False, statuses))
        return True if q else False
