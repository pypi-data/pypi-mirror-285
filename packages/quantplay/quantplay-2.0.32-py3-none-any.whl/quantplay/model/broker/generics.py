from typing import Literal, TypedDict
from typing_extensions import NotRequired

ExchangeType = Literal["NFO", "BFO", "NSE", "BSE", "MCX", "NCD", "BCD", "MFO"]
ProductType = Literal["NRML", "MIS", "CNC"]
OrderType = Literal["MARKET", "LIMIT", "SL"]
TransactionType = Literal["SELL", "BUY"]
InstrumentType = Literal["CE", "PE", "EQ", "FUT"]
StatusType = Literal["COMPLETE", "REJECTED", "CANCELLED", "TRIGGER PENDING", "OPEN"]


class ModifyOrderRequest(TypedDict):
    order_id: str
    variety: NotRequired[str]
    quantity: NotRequired[int]
    exchange: NotRequired[ExchangeType]
    trigger_price: float | None
    order_type: OrderType | None
    price: float


class UserBrokerProfileResponse(TypedDict):
    user_id: str
    full_name: NotRequired[str]
    segments: NotRequired[ExchangeType]
    exchanges: NotRequired[ExchangeType]
    email: NotRequired[str]
