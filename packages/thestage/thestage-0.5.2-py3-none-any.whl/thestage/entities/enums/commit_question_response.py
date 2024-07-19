from enum import Enum


class CommitQuestionResponse(str, Enum):
    COMMIT = "COMMIT"
    EXIT = "EXIT"
