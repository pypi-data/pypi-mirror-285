from typing import Literal, TypedDict


XTSExchangeSegmentType = Literal[1, 2, 3, 11, 12]


class XTSInstrumentType(TypedDict):
    exchangeSegment: XTSExchangeSegmentType
    exchangeInstrumentID: str | int


class XTSTypes:
    ExchangeSegmentType = XTSExchangeSegmentType
    XTSMessageCodeType = Literal[1501, 1502, 1505, 1507, 1510, 1512, 1105]
    PublishFormatType = Literal["JSON", "Binary"]
    ExchangeType = Literal["NSECM", "NSEFO", "NSECD", "BSECM", "BSEFO"]
    InstrumentType = XTSInstrumentType
    SeriesType = str
    OrderSide = Literal["BUY", "SELL"]
    OrderType = Literal["Market", "StopLimit", "StopMarket", "Limit"]
    ProductType = Literal["CO", "CNC", "MIS", "NRML"]
    PositionSqureOffModeType = Literal["DayWise", "NetWise"]
    PositionSquareOffQuantityTypeType = Literal["Percentage", "ExactQty"]
    DayOrNetType = Literal["DAY", "NET"]
