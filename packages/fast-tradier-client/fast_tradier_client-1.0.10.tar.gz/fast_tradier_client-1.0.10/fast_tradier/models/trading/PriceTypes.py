from enum import Enum

class EquityPriceType(str, Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"
    StopLimit = "stop_limit"

class OptionPriceType(str, Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"
    StopLimit = "stop_limit"

    Debit = "debit"
    Credit = "credit"
    Even = "even"