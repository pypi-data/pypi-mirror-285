from enum import Enum
from typing import List


class RentedStatusEnumDto(str, Enum):
    NEW: str = 'NEW'
    AWAITING_RENT: str = 'AWAITING_RENT'
    RENTING: str = 'RENTING'
    RENTED: str = 'RENTED'
    RENTING_FAILED: str = 'RENTING_FAILED'
    AWAITING_TERMINATE: str = 'AWAITING_TERMINATE'
    TERMINATING: str = 'TERMINATING'
    TERMINATED: str = 'TERMINATED'
    TERMINATING_FAILED: str = 'TERMINATING_FAILED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['RentedStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == RentedStatusEnumDto.ALL else False, statuses))
        return True if q else False
