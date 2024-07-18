from typing import List, Any, Dict
from investfly.api.RestApiClient import RestApiClient
from investfly.models.CommonModels import Message
from investfly.models.StrategyModels import TradingStrategyModel, BacktestResult


class StrategyApiClient:

    """
    Class used to make calls to /strategy endpoint to operate on trading strategies.
    """

    def __init__(self, restApiClient: RestApiClient) -> None:
        self.restApiClient = restApiClient

    def listStrategies(self) -> List[TradingStrategyModel]:
        strategiesList: List[Dict[str, Any]] = self.restApiClient.doGet('/strategy/list')
        strategiesList = list(filter(lambda jsonDict: jsonDict['type'] == 'SCRIPT', strategiesList))
        return list(map(lambda jsonDict: TradingStrategyModel.fromDict(jsonDict), strategiesList))

    def getStrategy(self, strategyId: int) -> TradingStrategyModel:
        strategyDict = self.restApiClient.doGet('/strategy/' + str(strategyId))
        return TradingStrategyModel.fromDict(strategyDict)

    def createStrategy(self, strategyModel: TradingStrategyModel) -> TradingStrategyModel:
        strategyDict = strategyModel.toDict()
        strategyDict['type'] = 'SCRIPT'
        strategyDict = self.restApiClient.doPost('/strategy/create', strategyDict)
        return TradingStrategyModel.fromDict(strategyDict)
        
    def updateStrategyCode(self, strategyId: int, code: str) -> str:
        return self.restApiClient.doPostCode('/strategy/' + str(strategyId) + '/update/code', code)

    def startBacktest(self, strategyId: int) -> Message:
        message = self.restApiClient.doPost(f'/backtest/{strategyId}/start', {})
        return Message.fromDict(message)

    def stopBacktest(self, strategyId: int) -> Message:
        message = self.restApiClient.doPost(f'/backtest/{strategyId}/stop', {})
        return Message.fromDict(message)

    def getBacktestResult(self, strategyId: int) -> BacktestResult:
        resultDict: Dict[str, Any] = self.restApiClient.doGet(f'/backtest/{strategyId}/result')
        return BacktestResult.fromDict(resultDict)

