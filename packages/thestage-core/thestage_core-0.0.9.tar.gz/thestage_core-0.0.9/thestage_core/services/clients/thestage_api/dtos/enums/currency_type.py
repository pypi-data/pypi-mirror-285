from enum import Enum


class CurrencyTypeEnumDto(str, Enum):
    ETHER: str = 'ETHER'
    STAGI: str = 'STAGI'
    USD: str = 'USD'
    EUR: str = 'EUR'
    USDT: str = 'USDT'
    UNKNOWN: str = 'UNKNOWN'
