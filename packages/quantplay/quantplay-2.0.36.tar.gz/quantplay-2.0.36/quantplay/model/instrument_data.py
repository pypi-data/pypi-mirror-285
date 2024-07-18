from typing import NotRequired, TypedDict

from quantplay.model.generics import ExchangeType


class InstrumentDataType(TypedDict):
    token: int
    exchange: ExchangeType
    broker_symbol: str
    tradingsymbol: str
    lot_size: float

    instrument_key: NotRequired[str]

    instrument_token: NotRequired[str]
    exchange_token: NotRequired[str]
