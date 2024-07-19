from enum import Enum


class CpuTypeEnumDto(str, Enum):
    INTEL: str = 'INTEL'
    AMD: str = 'AMD'
    ARM: str = 'ARM'
    UNKNOWN: str = 'UNKNOWN'
