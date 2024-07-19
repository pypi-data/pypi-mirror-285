from enum import Enum
from typing import List

import typer


# Deprecated, remove later
class SelfHostedStatusEnumDto(str, Enum):
    AWAITING_CONFIGURATION: str = 'AWAITING_CONFIGURATION'
    RUNNING: str = 'RUNNING'
    TERMINATED: str = 'TERMINATED'
    DELETED: str = 'DELETED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['SelfHostedStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == SelfHostedStatusEnumDto.ALL else False, statuses))
        return True if q else False


class SelfHostedBusinessStatusEnumDto(str, Enum):

    AWAITING_CONFIGURATION: str = 'AWAITING_CONFIGURATION'
    RUNNING: str = 'RUNNING'
    TERMINATED: str = 'TERMINATED'
    DELETED: str = 'DELETED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['SelfHostedBusinessStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == SelfHostedBusinessStatusEnumDto.ALL else False, statuses))
        return True if q else False
