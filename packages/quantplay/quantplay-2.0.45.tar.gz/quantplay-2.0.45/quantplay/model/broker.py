from typing import TypedDict

from typing_extensions import NotRequired

from quantplay.model.generics import ExchangeType, OrderTypeType

# **
# ** Requests
# **


class ModifyOrderRequest(TypedDict):
    order_id: str

    quantity: NotRequired[int]
    exchange: NotRequired[ExchangeType]
    trigger_price: NotRequired[float | None]
    order_type: NotRequired[OrderTypeType]
    price: NotRequired[float]


# **
# ** Responses
# **


class UserBrokerProfileResponse(TypedDict):
    user_id: str
    full_name: NotRequired[str]
    segments: NotRequired[ExchangeType]
    exchanges: NotRequired[ExchangeType]
    email: NotRequired[str]
