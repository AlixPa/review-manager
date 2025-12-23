from enum import Enum


class DateTimeFormat(str, Enum):
    Y_M_D = "%Y-%m-%d"
    Y_M_DTH_M_SZ = "%Y-%m-%dT%H:%M:%SZ"
    Y_M_D_H_M_S = "%Y-%m-%d %H:%M:%S"
    SQL = "%Y-%m-%d %H:%M:%S"
