from enum import Enum


class StorageTypeEnumDto(str, Enum):
    S3: str = 'S3'
    UNKNOWN: str = 'UNKNOWN'
