from enum import Enum


class GpuNameEnumDto(str, Enum):
    NVIDIA: str = 'NVIDIA'
    AMD: str = 'AMD'
    NO_GPU: str = 'NO_GPU'
    UNKNOWN: str = 'UNKNOWN'
