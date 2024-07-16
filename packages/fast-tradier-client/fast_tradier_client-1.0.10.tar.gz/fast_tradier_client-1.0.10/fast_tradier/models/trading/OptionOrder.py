from typing import Dict, List, Optional, Mapping, Any
from enum import Enum
from fast_tradier.models.trading.TOSTradierConverter import TOSTradierConverter
from fast_tradier.models.ModelBase import ModelBase
from fast_tradier.models.trading.Sides import OptionOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType
from fast_tradier.models.trading.Duration import Duration
from fast_tradier.models.trading.OrderBase import OrderBase
from fast_tradier.models.ModelBase import NewModelBase
from pydantic import BaseModel, ConfigDict, Field

class OptionLeg(NewModelBase):
    underlying_symbol: Optional[str] = None
    option_symbol: str
    quantity: int
    side: OptionOrderSide
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    def reverse_side(self) -> None:
        if self.side == OptionOrderSide.SellToOpen or self.side == OptionOrderSide.SellToOpen.value:
            self.side = OptionOrderSide.BuyToClose.value
        elif self.side == OptionOrderSide.BuyToOpen or self.side == OptionOrderSide.BuyToOpen.value:
            self.side = OptionOrderSide.SellToClose.value

class OptionOrderClass(str, Enum):
    SingleLeg = "option"
    MultiLegs = "multileg"

class OptionOrder(NewModelBase):
    symbol: str
    price: Optional[float] = None
    stop: Optional[float] = None
    price_type: OptionPriceType = Field(..., alias="type")
    duration: Duration
    option_legs: List[OptionLeg]
    side: Optional[OptionOrderSide] = None # required for single leg option order
    status: Optional[str] = "pending"
    id: Optional[int] = None
    tag: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    @property
    def ticker(self) -> str:
        """Convenience prop to get underlying symbol."""
        return self.symbol
    
    @property
    def order_class(self) -> Optional[str]:
        if len(self.option_legs) == 1:
            return OptionOrderClass.SingleLeg.value
        elif len(self.option_legs) > 1:
            return OptionOrderClass.MultiLegs.value

        return None

    def clone_option_legs(self, reverse_side: bool = False) -> List[OptionLeg]:
        '''deep clone option_legs'''
        cloned_legs = []
        for opt_leg in self.option_legs:
            leg = OptionLeg(**(opt_leg.to_json()))
            if reverse_side:
                leg.reverse_side()

            cloned_legs.append(leg)
        return cloned_legs
    
    def to_json(self) -> Mapping[str, Any]:
        """
        Override to_json so that the format complies to Tradier API.
        Returns:
            Mapping[str, Any]: _description_
        """
        temp_result = self.model_dump(by_alias=True)
        result: Dict[str, Any] = {}
        for k, v in temp_result.items():
            result[k] = v
        if self.option_legs is not None and len(self.option_legs) > 0:
            result["class"] = self.order_class
            if len(self.option_legs) == 1:
                result["option_symbol"] = self.option_legs[0].option_symbol
                result["side"] = self.option_legs[0].side
                result["quantity"] = self.option_legs[0].quantity
            elif len(self.option_legs) > 1:
                for i in range(len(self.option_legs)):
                    opt_item = self.option_legs[i]
                    symbol_key = f"option_symbol[{i}]"
                    result[symbol_key] = opt_item.option_symbol
                    side_key = f"side[{i}]"
                    result[side_key] = f"{opt_item.side}"
                    quant_key = f"quantity[{i}]"
                    result[quant_key] = f"{opt_item.quantity}"
        else:
            raise Exception("option legs should not be empty")

        return result