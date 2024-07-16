from typing import TypedDict

from typing_extensions import NotRequired

from quantplay.model.generics import ExchangeType, OrderTypeType


class ModifyOrderRequest(TypedDict):
    order_id: str
    variety: NotRequired[str]
    quantity: NotRequired[int]
    exchange: NotRequired[ExchangeType]
    trigger_price: float | None
    order_type: OrderTypeType | None
    price: float


class UserBrokerProfileResponse(TypedDict):
    user_id: str
    full_name: NotRequired[str]
    segments: NotRequired[ExchangeType]
    exchanges: NotRequired[ExchangeType]
    email: NotRequired[str]
