from typing import Dict, Tuple, Optional, Mapping, Any
from pydantic import Field, ConfigDict
from fast_tradier.models.ModelBase import ModelBase
from fast_tradier.models.ModelBase import NewModelBase

class TradierQuote(NewModelBase):
    symbol: str
    type_: str = Field(..., alias="type")
    open_price: Optional[float] = Field(..., alias="open")
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    last_price: Optional[float] = None
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    @property
    def ohlcv(self) -> Tuple:
        return self.open_price, self.high, self.low, self.close, self.volume

    @property
    def quote_type(self) -> str:
        return self.type_
    
    @property
    def mid(self) -> Optional[float]:
        return None if self.bid is None or self.ask is None else (self.bid + self.ask) / 2.0