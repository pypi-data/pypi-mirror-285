from enum import Enum


class AccessTypeEnumDto(str, Enum):
    SSH: str = 'SSH'
    UNKNOWN: str = 'UNKNOWN'
