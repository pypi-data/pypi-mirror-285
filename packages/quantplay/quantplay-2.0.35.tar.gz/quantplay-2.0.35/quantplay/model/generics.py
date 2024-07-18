from typing import Literal

ExchangeType = Literal["NFO", "BFO", "NSE", "BSE", "MCX", "NCD", "BCD", "MFO"]
ProductType = Literal["NRML", "MIS", "CNC"]
OrderTypeType = Literal["MARKET", "LIMIT", "SL", "SL-M"]
TransactionType = Literal["SELL", "BUY"]
InstrumentType = Literal["CE", "PE", "EQ", "FUT"]
OrderStatusType = Literal["COMPLETE", "REJECTED", "CANCELLED", "TRIGGER PENDING", "OPEN"]
