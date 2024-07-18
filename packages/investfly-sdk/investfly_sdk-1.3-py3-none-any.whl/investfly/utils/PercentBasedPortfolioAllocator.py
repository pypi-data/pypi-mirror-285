from typing import List

from investfly.models.PortfolioModels import Portfolio, PositionType, TradeOrder, TradeType
from investfly.models.StrategyModels import PortfolioSecurityAllocator, TradeSignal


class PercentBasedPortfolioAllocator(PortfolioSecurityAllocator):

    BROKER_FEE = 5.0

    def __init__(self, percent: float, positionType: PositionType) -> None:
        self.percent = percent
        self.positionType = positionType

    def allocatePortfolio(self, portfolio: Portfolio, tradeSignals: List[TradeSignal]) -> List[TradeOrder]:

        tradeType = TradeType.BUY if self.positionType == PositionType.LONG else TradeType.SHORT
        openPositionSecurities = {p.security for p in portfolio.openPositions if p.position == self.positionType}
        pendingOrdersSecurities = {o.security for o in portfolio.pendingOrders if o.tradeType == tradeType}
        openAndPendingSecurities = openPositionSecurities.union(pendingOrdersSecurities)

        tradeOrders: List[TradeOrder] = []

        buyingPower = portfolio.balances.buyingPower
        portfolioValue = portfolio.balances.currentValue
        allocatedAmountPerSecurity = (self.percent/100) * portfolioValue

        while buyingPower > allocatedAmountPerSecurity and len(tradeSignals) > 0:
            tradeSignal = tradeSignals.pop(0)
            if tradeSignal.security not in openAndPendingSecurities:
                tradeOrder = TradeOrder(tradeSignal.security, tradeType, maxAmount=allocatedAmountPerSecurity)
                tradeOrders.append(tradeOrder)
                buyingPower = buyingPower - allocatedAmountPerSecurity - PercentBasedPortfolioAllocator.BROKER_FEE

        return tradeOrders