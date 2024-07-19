from enum import Enum
from typing import List


class ContainerStatusEnumDto(str, Enum):
    FAILED: str = 'FAILED'
    BUSY: str = 'BUSY'
    DEAD: str = 'DEAD'
    CREATING: str = 'CREATING'
    CREATING_FAILED: str = 'CREATING_FAILED'
    STARTING: str = 'STARTING'
    RUNNING: str = 'RUNNING'
    STOPPING: str = 'STOPPING'
    STOPPED: str = 'STOPPED'
    RESTARTING: str = 'RESTARTING'
    DELETING: str = 'DELETING'
    DELETED: str = 'DELETED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['ContainerStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == ContainerStatusEnumDto.ALL else False, statuses))
        return True if q else False
