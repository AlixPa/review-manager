from enum import Enum


class TaskLinesOfCode(int, Enum):
    UNDER_100 = 1
    UNDER_500 = 2
    UNDER_1200 = 3
    ABOVE_1200 = 4
