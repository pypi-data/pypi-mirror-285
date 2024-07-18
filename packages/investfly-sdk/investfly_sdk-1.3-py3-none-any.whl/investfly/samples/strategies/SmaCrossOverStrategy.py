from typing import Dict, Any, List

from investfly.models import *
from investfly.utils import PercentBasedPortfolioAllocator


class SmaCrossOverStrategy(TradingStrategy):


    def getSecurityUniverseSelector(self) -> SecurityUniverseSelector:
        #return SecurityUniverseSelector.fromStockSymbols(["AAPL", "MSFT"])
        return SecurityUniverseSelector.fromStandardList(StandardSymbolsList.SP_100)

    @DataParams({
        "sma2": {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 2, "count": 2},
        "sma3": {"datatype": DataType.INDICATOR, "indicator": "SMA", "barinterval": BarInterval.ONE_MINUTE, "period": 3, "count": 2}
    })
    def evaluateOpenTradeCondition(self, security: Security, data: Dict[str, Any]) -> TradeSignal | None:
        # We asked for latest two values for each of these indicators so that we can implement a "crossover"
        # semantics, i.e, we generate trade signal when sma2 crosses over sma3
        sma2 = data["sma2"]
        sma3 = data["sma3"]
        if sma2[-1].value > sma3[-1].value and sma2[-2].value <= sma3[-2].value:
            return TradeSignal(security, PositionType.LONG)
        else:
            return None

    def getStandardCloseCondition(self) -> StandardCloseCriteria:
        return StandardCloseCriteria(targetProfit=1, stopLoss=-1, trailingStop=None,  timeOut=TimeDelta(60, TimeUnit.MINUTES))


    def processOpenTradeSignals(self, portfolio: Portfolio, tradeSignals: List[TradeSignal]) -> List[TradeOrder]:
        portfolioAllocator = PercentBasedPortfolioAllocator(5, PositionType.LONG)
        return portfolioAllocator.allocatePortfolio(portfolio, tradeSignals)

