from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, cast

from investfly.models.CommonModels import DatedValue
from investfly.models.MarketData import Security
from investfly.models.ModelUtils import ModelUtils

class PositionType(str, Enum):
    """ PositionType Enum """

    LONG = "LONG",
    SHORT = "SHORT"
    CLOSE = "CLOSE"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class TradeType(str, Enum):
    """Trade Type Enum """

    BUY = "BUY"
    SELL = "SELL"
    SHORT = "SHORT"
    COVER = "COVER"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class OrderType(str, Enum):
    """Order Type Enum """

    MARKET_ORDER = "MARKET_ORDER"
    LIMIT_ORDER = "LIMIT_ORDER"
    STOP_ORDER = "STOP_ORDER"
    ONE_CANCEL_OTHER = "ONE_CANCEL_OTHER"
    CUSTOM_CONDITION = "CUSTOM_CONDITION"


class Broker(str, Enum):

    """Broker Type Enum"""

    INVESTFLY = "INVESTFLY"
    TRADIER = "TRADIER"
    TDAMERITRADE = "TDAMERITRADE"
    BACKTEST = "BACKTEST"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclass
class TradeOrder:
    """ A class that represents a Trade Order """
    security: Security
    tradeType: TradeType
    orderType: OrderType = OrderType.MARKET_ORDER
    quantity: int | None = None
    maxAmount: float | None = None
    limitPrice: float | None = None # If left empty, will use latest quote as limit price

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        jsonDict["security"] = self.security.toDict()
        return jsonDict


@dataclass
class OrderStatus:
    """ Trade Order Status"""
    orderId: int
    status: str
    message: str | None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> OrderStatus:
        status = OrderStatus(jsonDict["orderId"], jsonDict["status"])
        status.message = jsonDict.get("message")
        return status


@dataclass
class PendingOrder(TradeOrder):
    orderId: str | None = None
    status: str | None = None
    scheduledDate: datetime | None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> Any:
        security = Security.fromDict(jsonDict["security"])
        pendingOrder = PendingOrder(security, TradeType(jsonDict["tradeType"]))
        pendingOrder.quantity = jsonDict.get("quantity")
        pendingOrder.maxAmount = jsonDict.get("maxAmount")
        pendingOrder.orderId = jsonDict.get("orderId")
        pendingOrder.status = jsonDict.get("status")
        pendingOrder.scheduledDate = ModelUtils.parseZonedDatetime(cast(str, jsonDict.get("scheduledDate")))
        return pendingOrder


@dataclass()
class Balances:
    buyingPower: float
    cashBalance: float
    currentValue: float
    initialAmount: float | None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> Balances:
        balances = Balances(jsonDict["buyingPower"],
                            jsonDict["cashBalance"],
                            jsonDict["currentValue"])
        balances.initialAmount = jsonDict.get("initialAmount")
        return balances


@dataclass
class CompletedTrade:
    security: Security
    date: datetime
    price: float
    quantity: int
    tradeType: TradeType

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> CompletedTrade:
        security = Security.fromDict(jsonDict["security"])
        date = ModelUtils.parseZonedDatetime(jsonDict["date"])
        return CompletedTrade(security, date, jsonDict["price"], jsonDict["quantity"], TradeType[jsonDict["tradeType"]])


@dataclass
class ClosedPosition:
    security: Security
    position: PositionType
    openDate: datetime
    closeDate: datetime
    openPrice: float
    closePrice: float
    quantity: int
    profitLoss: float|None = None
    percentChange: float| None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> ClosedPosition:
        security = Security.fromDict(jsonDict['security'])
        position = PositionType[jsonDict['position']]
        openDate = ModelUtils.parseZonedDatetime(jsonDict['openDate'])
        closeDate = ModelUtils.parseZonedDatetime((jsonDict['closeDate']))
        openPrice = jsonDict['openPrice']
        closePrice = jsonDict['closePrice']
        quantity = jsonDict['quantity']

        closedPosition =  ClosedPosition(security, position, openDate, closeDate, openPrice, closePrice, quantity)
        if "profitLoss" in jsonDict:
            closedPosition.profitLoss = jsonDict['profitLoss']
        if "percentChange" in jsonDict:
            closedPosition.percentChange = jsonDict['percentChange']

        return closedPosition

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        jsonDict["security"] = self.security.toDict()
        jsonDict["position"] = self.position.value
        jsonDict["openDate"] = ModelUtils.formatZonedDatetime(self.openDate)
        jsonDict["closeDate"] = ModelUtils.formatZonedDatetime((self.closeDate))
        return jsonDict

@dataclass
class OpenPosition:
    security: Security
    position: PositionType
    avgPrice: float
    quantity: int
    purchaseDate: datetime
    currentPrice: float | None = None
    currentValue: float | None = None
    profitLoss: float | None = None
    percentChange: float | None = None

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> OpenPosition:
        security = Security.fromDict(jsonDict["security"])
        openPos = OpenPosition(security,
                               PositionType(jsonDict["position"]),
                               jsonDict["avgPrice"],
                               jsonDict["quantity"],
                               ModelUtils.parseZonedDatetime(jsonDict["purchaseDate"])
                               )
        openPos.currentPrice = jsonDict.get("currentPrice")
        openPos.currentValue = jsonDict.get("currentValue")
        openPos.profitLoss = jsonDict.get("profitLoss")
        openPos.percentChange = jsonDict.get("percentChange")
        return openPos

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        jsonDict["security"] = self.security.toDict()
        jsonDict["purchaseDate"] = ModelUtils.formatZonedDatetime(self.purchaseDate)
        return jsonDict


class Portfolio:
    def __init__(self, portfolioId: str, broker: Broker, balances: Balances) -> None:
        self.portfolioId = portfolioId
        self.broker = broker
        self.balances: Balances = balances
        self.openPositions: List[OpenPosition] = []
        self.pendingOrders: List[PendingOrder] = []
        self.completedTrades: List[CompletedTrade] = []

    def __str__(self) -> str:
        json_dict = self.__dict__.copy()
        json_dict["openPositions"] = len(self.openPositions)
        json_dict["completedTrades"] = len(self.completedTrades)
        json_dict["pendingOrders"] = len(self.pendingOrders)
        return str(json_dict)

    def __repr__(self):
        return self.__str__()


@dataclass
class PortfolioPerformance:
    netReturn: float|None = None
    annualizedReturn: float|None = None
    profitFactor: float|None = None

    totalTrades: int | None = None
    winRatioPct: float| None = None
    avgProfitPerTradePct: float| None = None
    avgLossPerTradePct: float| None = None

    meanReturnPerTradePct: float | None = None
    sharpeRatioPerTrade: float | None = None

    maxDrawdownPct: float|None = None
    portfolioValues: List[DatedValue]|None = None

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        if self.portfolioValues is not None:
            jsonDict["portfolioValues"] = [dv.toJsonDict() for dv in self.portfolioValues]
        else:
            jsonDict['portfolioValues'] = []
        return jsonDict

    @staticmethod
    def fromDict(jsonDict: Dict[str, Any]) -> PortfolioPerformance:
        perf = PortfolioPerformance()
        for key, value in jsonDict.items():
            setattr(perf, key, value)
        if 'portfolioValues' in jsonDict:
            perf.portfolioValues = [ DatedValue.fromDict(dv) for dv in jsonDict['portfolioValues']]
        else:
            perf.portfolioValues = []
        return perf

    def __str__(self):
        jsonDict = self.__dict__.copy()
        if 'portfolioValues' in jsonDict:
            del jsonDict['portfolioValues']
        return str(jsonDict)

    def __repr__(self):
        return self.__str__()
