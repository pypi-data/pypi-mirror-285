import json
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, List, Any
from pydantic import Field, ConfigDict
from fast_tradier.models.DataClassModelBase import DataClassModelBase
from fast_tradier.models.ModelBase import NewModelBase

class Leg(NewModelBase):
    id: int
    type: str
    symbol: str
    side: str
    quantity: float
    status: str
    duration: str
    price: Optional[float] = None
    avg_fill_price: Optional[float] = None
    exec_quantity: float = 0
    last_fill_price: Optional[float] = None
    last_fill_quantity: float = 0
    remaining_quantity: float = 0
    create_date: str
    transaction_date: str
    # class: str
    class_: Optional[str] = Field(..., alias="class")
    option_symbol: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)
    
    def to_json(self) -> Mapping[str, Any]:
        result = self.model_dump(by_alias=True)
        return result

class AccountOrder(NewModelBase):
    id: int
    # type: str
    type_: str = Field(..., alias="type")
    symbol: str
    side: str
    quantity: float
    status: str
    duration: str
    price: Optional[float] = None
    avg_fill_price: Optional[float] = None
    exec_quantity: Optional[float] = None
    last_fill_price: Optional[float] = None
    last_fill_quantity: Optional[float] = None
    remaining_quantity: Optional[float] = None
    create_date: Optional[str] = None
    transaction_date: Optional[str] = None
    # class_type: str
    class_: Optional[str] = Field(..., alias="class")
    num_legs: Optional[int] = None
    strategy: Optional[str] = None
    leg: Optional[List[Leg]] = []
    stop_price: Optional[float] = None
    reason_description: Optional[float] = None # rejection details
    tag: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

    def to_json(self) -> Mapping[str, Any]:
        result = self.model_dump(by_alias=True)
        return result