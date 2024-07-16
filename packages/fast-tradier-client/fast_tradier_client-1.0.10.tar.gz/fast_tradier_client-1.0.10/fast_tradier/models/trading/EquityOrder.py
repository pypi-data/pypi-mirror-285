from fast_tradier.models.ModelBase import ModelBase
from typing import List, Dict, Optional
from fast_tradier.models.trading.Sides import EquityOrderSide
from fast_tradier.models.trading.PriceTypes import EquityPriceType
from fast_tradier.models.trading.Duration import Duration
from fast_tradier.models.trading.OrderBase import OrderBase
from pydantic import Field

class EquityOrder(OrderBase):
    clazz: str = Field(..., alias="class")
    symbol: str
    side: EquityOrderSide
    quantity: float
    duration: Duration
    price: Optional[float] = None
    price_type: EquityPriceType = Field(..., alias="type")
    stop: Optional[float] = None
    tag: Optional[str] = None

    @property
    def ticker(self) -> str:
        return self.symbol