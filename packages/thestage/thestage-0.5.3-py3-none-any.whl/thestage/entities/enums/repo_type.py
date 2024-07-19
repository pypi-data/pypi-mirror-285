from enum import Enum


class RepoType(str, Enum):
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    UNKNOWN = "UNKNOWN"
