from enum import Enum


class TaskStatus(str, Enum):
    FAILURE = "failure"
    RUNNING = "running"
    SUCCESS = "success"
    TIMED_OUT = "timed_out"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
