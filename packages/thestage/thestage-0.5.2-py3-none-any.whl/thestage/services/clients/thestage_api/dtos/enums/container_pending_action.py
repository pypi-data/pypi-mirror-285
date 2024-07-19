from enum import Enum


class ContainerPendingActionEnumDto(str, Enum):
    CREATE: str = 'CREATE'
    UPDATE: str = 'UPDATE'
    START: str = 'START'
    RESTART: str = 'RESTART'
    STOP: str = 'STOP'
    DELETE: str = 'DELETE'
    UNKNOWN: str = 'UNKNOWN'
