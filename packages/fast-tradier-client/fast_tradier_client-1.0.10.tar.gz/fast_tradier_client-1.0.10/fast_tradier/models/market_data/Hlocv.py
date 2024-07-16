from dataclasses import dataclass
from typing import Dict, Optional, Mapping, Any
from pydantic import ConfigDict, Field

from fast_tradier.models.DataClassModelBase import DataClassModelBase
from fast_tradier.models.ModelBase import NewModelBase

class Hlocv(NewModelBase):
    date: str
    open_price: Optional[float] = Field(..., alias="open")
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)