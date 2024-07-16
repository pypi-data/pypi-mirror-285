from dataclasses import dataclass
from typing import Dict, Optional, Mapping, Any
from datetime import datetime
from pydantic import ConfigDict, Field
from fast_tradier.utils.TimeUtils import TimeUtils
from fast_tradier.models.ModelBase import NewModelBase
from fast_tradier.models.DataClassModelBase import DataClassModelBase

class Quote(NewModelBase):
    symbol: str
    description: Optional[str] = None
    exch: Optional[str] = None
    type_: str = Field(..., alias="type")
    last: Optional[float] = None
    change: Optional[float] = None
    volume: Optional[float] = None
    open_price: Optional[float] = Field(..., alias="open")
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    underlying: Optional[str] = None
    strike: Optional[float] = None
    change_percentage: Optional[float] = None
    average_volume: Optional[int] = None
    last_volume: Optional[int] = None
    trade_date: Optional[int] = None
    prevclose: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    bidsize: Optional[int] = None
    bidexch: Optional[str] = None
    bid_date: Optional[int] = None
    asksize: Optional[int] = None
    askexch: Optional[str] = None
    ask_date: Optional[int] = None
    open_interest: Optional[int] = None
    contract_size: Optional[int] = None
    expiration_date: Optional[str] = None
    expiration_type: Optional[str] = None
    option_type: Optional[str] = None
    root_symbol: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    @property
    def is_option(self) -> bool:
        return self.type.upper() == 'OPTION'

    @property
    def is_stock(self) -> bool:
        return self.type.upper() == 'STOCK'

    @property
    def trade_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.trade_date)

    @property
    def bid_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.bid_date)

    @property
    def ask_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.ask_date)