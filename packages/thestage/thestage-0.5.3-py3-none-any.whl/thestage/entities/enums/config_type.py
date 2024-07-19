from enum import Enum


class ConfigType(str, Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"
    #ENV = "ENV"
    UNKNOWN = "UNKNOWN"
