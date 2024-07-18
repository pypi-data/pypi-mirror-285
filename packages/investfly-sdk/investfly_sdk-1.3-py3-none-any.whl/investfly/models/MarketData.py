from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypedDict, Dict, Any, cast

from investfly.models.CommonModels import DatedValue
from investfly.models.MarketDataIds import QuoteField

def parseDatetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def formatDatetime(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


class SecurityType(str, Enum):
    """
    Enum representing Security Type (STOCK, ETF)
    """

    STOCK = "STOCK"
    ETF = "ETF"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


# All enums subclass str to make them JSON serializable

@dataclass(frozen=True)
class Security:
    """
    Class representing a security instrument that is traded in the market
    """

    symbol: str
    """ Security Symbol """

    securityType: SecurityType
    """ Security Type """

    @staticmethod
    def createStock(symbol: str):
        return Security(symbol, SecurityType.STOCK)

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> Security:
        return Security(jsonDict["symbol"], SecurityType[jsonDict["securityType"]])

    def toDict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Quote:
    """ Class representing Price Quote """
    symbol: str
    date: datetime
    lastPrice: float
    prevClose: float| None = None
    todayChange: float | None = None
    todayChangePercent: float | None = None
    dayOpen: float | None = None
    dayHigh: float | None = None
    dayLow: float | None = None
    dayVolume: int | None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> Quote:
        quote = Quote(jsonDict["symbol"], parseDatetime(jsonDict["date"]), jsonDict["lastPrice"])
        quote.prevClose = jsonDict.get('prevClose')
        quote.todayChange = jsonDict.get("todayChange")
        quote.todayChangePercent = jsonDict.get('todayChangePercent')
        quote.dayOpen = jsonDict.get('dayOpen')
        quote.dayHigh = jsonDict.get('dayHigh')
        quote.dayLow = jsonDict.get('dayLow')
        return quote

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        jsonDict["date"] = formatDatetime(self.date)
        return jsonDict

    def toIndicatorValue(self, quoteField: QuoteField) -> DatedValue:
        if quoteField == QuoteField.LASTPRICE:
            return DatedValue(self.date, self.lastPrice)
        elif quoteField == QuoteField.DAY_OPEN:
            if self.dayOpen is None:
                raise Exception("DAY_OPEN price not available in Quote")
            return DatedValue(self.date, self.dayOpen)
        elif quoteField == QuoteField.DAY_HIGH:
            if self.dayHigh is None:
                raise Exception("DAY_HIGH price not available in Quote")
            return DatedValue(self.date, self.dayHigh)
        elif quoteField == QuoteField.DAY_LOW:
            if self.dayLow is None:
                raise Exception("DAY_LOW price not available in Quote")
            return DatedValue(self.date, self.dayLow)
        elif quoteField == QuoteField.PREV_DAY_CLOSE:
            if self.prevClose is None:
                raise Exception("PREV_DAY_CLOSE price not available in Quote")
            return DatedValue(self.date, self.prevClose)
        elif quoteField == QuoteField.DAY_CHANGE:
            if self.todayChange is None:
                raise Exception("DAY_CHANGE not available in Quote")
            return DatedValue(self.date, self.todayChange)
        elif quoteField == QuoteField.DAY_CHANGE_PCT:
            if self.todayChangePercent is None:
                raise Exception("DAY_CHANGE_PCT value not available in Quote")
            return DatedValue(self.date, self.todayChangePercent)
        elif quoteField == QuoteField.DAY_VOLUME:
            if self.dayVolume is None:
                raise Exception("DAY_VOLUME not available in Quote")
            return DatedValue(self.date, self.dayVolume)
        else:
            raise Exception("Invalid Quote Indicator ID: " + quoteField)

    def toEODBar(self) -> Bar:
        bar = Bar()
        bar['symbol'] = self.symbol
        bar['barinterval'] = BarInterval.ONE_DAY
        bar['date'] = self.date.replace(second=0, microsecond=0)
        bar['open'] = cast(float, self.dayOpen)
        bar['high'] = cast(float, self.dayHigh)
        bar['low'] = cast(float, self.dayLow)
        bar['close'] = cast(float, self.lastPrice)
        bar['volume'] = cast(int, self.dayVolume)
        return bar


class BarInterval(str, Enum):
    """ Enum to represent BarInterval """
    ONE_MINUTE = "ONE_MINUTE"
    FIVE_MINUTE = "FIVE_MINUTE"
    FIFTEEN_MINUTE = "FIFTEEN_MINUTE"
    THIRTY_MINUTE = "THIRTY_MINUTE"
    SIXTY_MINUTE = "SIXTY_MINUTE"
    ONE_DAY = "ONE_DAY"

    def getMinutes(self) -> int:
        if self == BarInterval.ONE_MINUTE:
            return 1
        elif self == BarInterval.FIVE_MINUTE:
            return 5
        elif self == BarInterval.FIFTEEN_MINUTE:
            return 15
        elif self == BarInterval.THIRTY_MINUTE:
            return 30
        elif self == BarInterval.SIXTY_MINUTE:
            return 60
        else:
            return 24 * 60



Bar = TypedDict("Bar", {"symbol": str,
                        "barinterval": BarInterval,
                        "date": datetime,
                        "open": float,
                        "close": float,
                        "high": float,
                        "low": float,
                        "volume": int
                        },
                total=False)

@dataclass
class StockNews:
    date: datetime
    title: str
    description: str


class NoDataException(Exception):
    def __init__(self,  dataParams: Dict[str, Any]):
        self.message = f"Data Not Available: {dataParams}"

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.message
