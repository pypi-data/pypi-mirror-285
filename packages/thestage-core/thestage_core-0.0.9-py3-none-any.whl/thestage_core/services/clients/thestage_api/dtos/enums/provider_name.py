from enum import Enum


class ProviderNameEnumDto(str, Enum):
    Amazon: str = 'Amazon'
    DigitalOcean: str = 'DigitalOcean'
    Exoscale: str = 'Exoscale'
    Vultr: str = 'Vultr'
    UNKNOWN: str = 'UNKNOWN'
