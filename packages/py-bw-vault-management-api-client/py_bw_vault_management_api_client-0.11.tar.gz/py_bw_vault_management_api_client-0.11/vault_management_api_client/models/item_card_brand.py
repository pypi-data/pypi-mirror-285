from enum import Enum


class ItemCardBrand(str, Enum):
    VISA = "visa"

    def __str__(self) -> str:
        return str(self.value)
