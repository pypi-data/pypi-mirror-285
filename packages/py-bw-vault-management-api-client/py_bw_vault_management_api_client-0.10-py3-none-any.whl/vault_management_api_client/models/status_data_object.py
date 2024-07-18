from enum import Enum


class StatusDataObject(str, Enum):
    TEMPLATE = "template"

    def __str__(self) -> str:
        return str(self.value)
