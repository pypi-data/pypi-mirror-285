from enum import Enum


class StatusDataTemplateStatus(str, Enum):
    LOCKED = "locked"
    UNAUTHENTICATED = "unauthenticated"
    UNLOCKED = "unlocked"

    def __str__(self) -> str:
        return str(self.value)
