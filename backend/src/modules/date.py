from datetime import date, timedelta
from enum import Enum


class DayOfTheWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def get_first_day_of_cycle(
    cycle_offset: int = 0, cycle_start_day: DayOfTheWeek = DayOfTheWeek.TUESDAY
) -> date:
    """
    Cycle offset goes backward.
    cycle_offset = 0 -> current cycle
    cycle_offset = 1 -> previous cycle
    """
    return date.today() - timedelta(
        days=(date.today().weekday() - cycle_start_day.value) % 7 + (7 * cycle_offset)
    )
