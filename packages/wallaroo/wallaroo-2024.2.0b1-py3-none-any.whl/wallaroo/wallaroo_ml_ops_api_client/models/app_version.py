from enum import Enum


class AppVersion(str, Enum):
    VALUE_0 = "2024.1.0"

    def __str__(self) -> str:
        return str(self.value)
