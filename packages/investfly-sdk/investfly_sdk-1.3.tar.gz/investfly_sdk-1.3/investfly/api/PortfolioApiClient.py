from typing import Any, Dict

from investfly.api.RestApiClient import RestApiClient
from investfly.models.PortfolioModels import Broker, Portfolio, Balances, OpenPosition, CompletedTrade, PendingOrder, \
    TradeOrder, OrderStatus


class PortfolioApiClient:
    """
    This class is intended to make REST API calls to /portfolio endpoint to get information on virtual portfolio
    and connected brokerage account
    """

    def __init__(self, restApiClient: RestApiClient) -> None:
        self.restApiClient = restApiClient

    def getPortfolio(self, portfolioId: str, broker: Broker) -> Portfolio:
        portfolioDict: Dict[str, Any] = self.restApiClient.doGet(f"/portfolio/{broker.value}/{portfolioId}")
        balances = Balances.fromDict(portfolioDict)
        portfolio = Portfolio(portfolioDict["portfolioId"], Broker(portfolioDict["broker"]), balances)

        openPosList = self.restApiClient.doGet(f'/portfolio/{broker.value}/{portfolioId}/portfoliostocks')
        for openPosDict in openPosList:
            portfolio.openPositions.append(OpenPosition.fromDict(openPosDict))

        completedTradesList = self.restApiClient.doGet(f'/portfolio/{broker.value}/{portfolioId}/trades')
        for compTradeDict in completedTradesList:
            portfolio.completedTrades.append(CompletedTrade.fromDict(compTradeDict))

        pendingOrdersList = self.restApiClient.doGet(f'/portfolio/{broker.value}/{portfolioId}/pending')
        for pendingOrderDict in pendingOrdersList:
            portfolio.pendingOrders.append(PendingOrder.fromDict(pendingOrderDict))

        return portfolio

    def submitTradeOrder(self, portfolioId: str, broker: Broker, order: TradeOrder) -> OrderStatus:
        res = self.restApiClient.doPost(f'/portfolio/{broker.value}/{portfolioId}/trade', order.toDict())
        return OrderStatus.fromDict(res)



