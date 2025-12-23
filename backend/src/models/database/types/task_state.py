from enum import Enum


class TaskState(int, Enum):
    PENDING_REVIEW = 1
    PENDING_CHANGES = 2
    APPROVED = 3
