# This is a self-documenting starter template to define custom trading strategy in Python Programming Language
# This code can be used as-it-is to try a new strategy

# Following two imports are required
from investfly.models import *
from investfly.utils import *

# Import basic types, they aren't required but recommended
from typing import Any, List, Dict

# Following numeric analysis imports are allowed
import math
import statistics
import numpy as np
import talib  # https://pypi.org/project/TA-Lib/
import pandas
# ! WARN ! Imports other than listed above are disallowed and won't pass validation

# Create a class that extends TradingStrategy and implement 5 methods shown below
class SmaCrossOverTemplate(TradingStrategy):

    def getSecurityUniverseSelector(self) -> SecurityUniverseSelector:
        # Narrow down the scope (or universe of stocks) against which to run this strategy. We support 3 options
        # 1. Standard List: SP_100, SP_500, NASDAQ_100, NASDAQ_COMPOSITE, RUSSELL_1000,DOW_JONES_INDUSTRIALS, ETFS
        # universe = SecurityUniverseSelector.fromStandardList(StandardSymbolsList.SP_100)
        # 2. Custom List
        # universe = SecurityUniverseSelector.fromStockSymbols(['AAPL', 'MSFT'])
        # 3. Financial Query (Dynamic List)
        financialQuery = FinancialQuery()  # MARKETCAP > 1B AND PE > 20
        financialQuery.addCondition(FinancialCondition(FinancialField.MARKET_CAP, ComparisonOperator.GREATER_THAN, "1B"))
        financialQuery.addCondition(FinancialCondition(FinancialField.PRICE_TO_EARNINGS_RATIO, ComparisonOperator.GREATER_THAN, "20"))
        universe = SecurityUniverseSelector.fromFinancialQuery(financialQuery)
        return universe


    """
    The function evaluateOpenTradeCondition below must be annotated with OnData to indicate when should this function be called and what values to pass
    This function is called separately for each security
    @WithData({
        "sma2":             {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE,  "period": 2, "count": 2},
        "sma3":             {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 3, "count": 2},
        "allOneMinBars":    {"datatype": DataType.BARS, "barinterval": BarInterval.ONE_MINUTE},
        "latestDailyBar":   {"datatype": DataType.BARS, "barinterval": BarInterval.ONE_DAY, "count":1},
        "quote":            {"datatype": DataType.QUOTE},
        "lastprice":        {"datatype": DataType.QUOTE, "field": QuoteField.LASTPRICE},
        "allFinancials":    {"datatype": DataType.FINANCIAL},
        "revenue":          {"datatype": DataType.FINANCIAL, "field": FinancialField.REVENUE}
    })
    """
    @DataParams({
        "sma5": {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 2, "count": 2},
        "ema14": {"datatype": DataType.INDICATOR, "indicator": "EMA", "barinterval": BarInterval.ONE_MINUTE, "period": 14, "count": 2}
    })
    def evaluateOpenTradeCondition(self, security: Security, data: Dict[str, Any]) -> TradeSignal | None:
        """
        :param security: The stock security against which this is evaluated. You use it to construct TradeSignal
        :param data: Dictionary with the requested data based on @DataParams annotation. The keys in the dictionary
        match the keys specified in @DataParams annotation ('sma5', and 'ema14' in this case)
        The data type of the value depends on datatype. Most common in DatedValue object which has two props: date and value
         datatype=INDICATOR, value type = DatedValue
         datatype=QUOTE, field is specified, value type = DatedValue
         datatype=QUOTE, field is not specified, value type is Quote object (has dayOpen, dayHigh, dayLow, prevOpen etc)
         datatype=BARS, value type is BAR
        Further, if the count is specified and greater than 1, value is returned as a List
        :return:  TradeSignal if open condition matches and to signal open trade, None if open trade condition does not match
        """

        # We asked for latest two values for each of these indicators so that we can implement a "crossover"
        # semantics, i.e generate trade signal when sma2 crosses over ema14 (i.e sma5 was below ema14 at previous bar
        # but it is higher in this bar).

        # The other way to implement crossover effect is by storing previous result in state as described below
        sma5 = data["sma5"]
        ema14 = data["ema14"]
        if sma5[-1].value > ema14[-1].value and sma5[-2].value <= ema14[-2].value:
            # when current sma4 > ema14 and previous sma5 <= ema14, return a TradeSignal.
            # TradeSignal can optionally set TradeSignal.strength to indicate strength of the signal
            return TradeSignal(security, PositionType.LONG)
        else:
            return None

    def processOpenTradeSignals(self, portfolio: Portfolio, tradeSignals: List[TradeSignal]) -> List[TradeOrder]:
        """
        In this method, you convert the TradeSignals into TradeOrders. You must do this for couple reasons:
           1. Assume 1000 stocks match the open trade condition and so you have 1000 TradeSignals, but that does not
           mean that you want to open position for 1000 stocks in your portfolio. You may want to order those trade signals
           by strength and limit to top 10 trade signals
           2. Your portfolio may already have open position for a stock corresponding to particular trade signal. In that case,
           you may wan to skip that trade signal, and prioritize opening new position for other stocks
           3. Here, you also set TradeOrder speficiations such as order type, quantity etc
           4. You may want to fully rebalance portfolio baseed on these new trade signals
        :param portfolio:  Current portfolio state
        :param tradeSignals: Trade Signals correspoding to stocks matching open trade condition
        :return:  List of TradeOrders to execute
        """

        # We provide a convenience utility that allocates given percent (10% set below) of portfolio in the given stock
        portfolioAllocator = PercentBasedPortfolioAllocator(10, PositionType.LONG)
        return portfolioAllocator.allocatePortfolio(portfolio, tradeSignals)

    def getStandardCloseCondition(self) -> StandardCloseCriteria | None:
        # TargetProfit, StopLoss, Timeout are standard close/exit criteria. TargetProfit and StopLoss are specified in percentages
        return StandardCloseCriteria(targetProfit=5, stopLoss=-5, trailingStop=None, timeOut=TimeDelta(10, TimeUnit.DAYS))


    @DataParams({
        "sma5": {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 2},
        "ema14": {"datatype": DataType.INDICATOR, "indicator": "EMA", "barinterval": BarInterval.ONE_MINUTE, "period": 14}
    })
    def evaluateCloseTradeCondition(self, openPos: OpenPosition, data: Dict[str, Any]) -> TradeOrder | None:
        """
        Implementing this method is optional. But when implemented, it should be implemented similar to evaluateOpenTradeCondition
        :param openPos: The open position
        :param data: Requested data that corresponds to the open position's security symbol
        :return: TradeOrder if the position is supposed to be closed, None otherwise
        """

        # Note that unlike in evalOpenTradeCondition, "count" is omitted for both sma5 and ema14 DataParams. When
        # count is omitted, it defaults to count=1, which means we will get a single DatedValue instead of List[DatedValue]

        # For close conditions, implementing crossover effect is not required because the first time the condition
        # defined below is met and TradeOrder is returned to close the position, closeOrder will be submitted and this
        # method is never called on the same open position again

        sma5 = data["sma5"]
        ema14 = data["ema14"]

        if sma5.value < 0.9 * ema14.value:
            return TradeOrder(openPos.security, TradeType.SELL)
        else:
            return None
