from enum import Enum


class TaskReviewPriority(int, Enum):
    FULL_REVIEW = 1
    BASED_ON_EVIDENCE = 2
    APPROVE_ONLY = 3
