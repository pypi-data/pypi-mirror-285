from dataclasses import dataclass
from typing import Dict, Optional
from fast_tradier.models.ModelBase import NewModelBase
from fast_tradier.models.DataClassModelBase import DataClassModelBase

class Position(NewModelBase):
    cost_basis: Optional[float] = None
    date_acquired: Optional[str] = None
    id: int
    quantity: Optional[float] = None
    symbol: str