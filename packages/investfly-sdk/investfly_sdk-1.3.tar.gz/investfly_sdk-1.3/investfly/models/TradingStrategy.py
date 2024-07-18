from abc import ABC, abstractmethod
from typing import List, Any, Dict

from investfly.models.MarketData import Security
from investfly.models.SecurityUniverseSelector import SecurityUniverseSelector
from investfly.models.StrategyModels import TradeSignal, StandardCloseCriteria
from investfly.models.PortfolioModels import TradeOrder, OpenPosition, Portfolio, PositionType
from investfly.utils.PercentBasedPortfolioAllocator import PercentBasedPortfolioAllocator


class TradingStrategy(ABC):
    """
    This is the main interface (abstract class) used to implement a trading strategy.
    """

    def __init__(self) -> None:
        self.state: Dict[str, int | float | bool] = {}
        """The persisted state of the strategy. """

    @abstractmethod
    def getSecurityUniverseSelector(self) -> SecurityUniverseSelector:
        """
        This function is used to narrow down the set of securities (i.e stocks) against which to run your logic.
        You can pick one of the standard list (e.g SP100) that we provide, provide your own list with comma separated symbols list,
        or provide a query based on fundamental metrics like MarketCap, PE Ratio etc.
        See docs on
        `investfly.models.SecurityUniverseSelector.SecurityUniverseSelector` for more details.
        Returns
        :return: `investfly.models.SecurityUniverseSelector.SecurityUniverseSelector`
        """
        pass


    @abstractmethod
    def evaluateOpenTradeCondition(self, security: Security, data: Dict[str, Any]) -> TradeSignal | None:
        """
        This function must be annotated with @DataParams to indicate what data (i.e indicator values) are needed as shown below.
        The function is called whenever a new data is available based on the subscribed data.
        This function is called separately for each security.
        ```
        @DataParams({
            "sma2":             {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE,  "period": 2, "count": 2},
            "sma3":             {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 3, "count": 2},
            "allOneMinBars":    {"datatype": DataType.BARS, "barinterval": BarInterval.ONE_MINUTE},
            "latestDailyBar":   {"datatype": DataType.BARS, "barinterval": BarInterval.ONE_DAY, "count":1},
            "quote":            {"datatype": DataType.QUOTE},
            "lastprice":        {"datatype": DataType.QUOTE, "field": QuoteField.LASTPRICE},
            "allFinancials":    {"datatype": DataType.FINANCIAL},
            "revenue":          {"datatype": DataType.FINANCIAL, "field": FinancialField.REVENUE}

        })
        ```
        :param security: The stock security against which this is evaluated. You use it to construct TradeSignal
        :param data: Dictionary with the requested data based on @DataParams annotation.

        The keys of the data param dictionary match the keys specified in @DataParams annotation. The value depends on the datatype parameter.
         datatype=INDICATOR, value type = `investfly.models.CommonModels.DatedValue`
         datatype=QUOTE, field is specified, value type = `investfly.models.CommonModels.DatedValue`
         datatype=QUOTE, field is not specified, value type is `investfly.models.MarketData.Quote` object (has dayOpen, dayHigh, dayLow, prevOpen etc)
         datatype=BARS, value type is `investfly.models.MarketData.Bar`

        Further, if the count is specified and greater than 1, value is returned as a List
        :return:  `investfly.model.StrategyModels.TradeSignal` if open condition matches and to signal open trade, None if open trade condition does not match
        """
        pass

    def processOpenTradeSignals(self, portfolio: Portfolio, tradeSignals: List[TradeSignal]) -> List[TradeOrder]:
        """
        This method is used to convert TradeSignals into TradeOrders. You must do this for couple reasons:
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
        portfolioAllocator = PercentBasedPortfolioAllocator(10, PositionType.LONG)
        return portfolioAllocator.allocatePortfolio(portfolio, tradeSignals)

    def getStandardCloseCondition(self) -> StandardCloseCriteria | None:
        """
        TargetProfit, StopLoss, TrailingStop and Timeout are considered as standard close criteria. This function
        is created so that you can specify those standard close/exit conditions easily
        :return: `investfly.models.StrategyModels.StandardCloseCriteria`
        """
        # Note that these are always executed as MARKET_ORDER
        return None

    def evaluateCloseTradeCondition(self, openPos: OpenPosition, data) -> TradeOrder | None:
        """
        Implementing this method is optional. But when implemented, it should be implemented similar to evaluateOpenTradeCondition
        :param openPos: The open position
        :param data: Requested data that corresponds to the open position's security symbol
        :return: TradeOrder if the position is supposed to be closed, None otherwise
        """
        return None

    def runAtInterval(self, portfolio: Portfolio) -> List[TradeOrder]:
        return []

    # These are optional methods that strategy can implement to track states between executions
    def getState(self) -> Dict[str, int | float | bool]:
        return self.state

    def restoreState(self, state: Dict[str, int | float | bool]) -> None:
        self.state = state
