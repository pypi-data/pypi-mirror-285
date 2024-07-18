from typing import List, Dict, Any

from investfly.api.RestApiClient import RestApiClient
from investfly.models import IndicatorSpec


class IndicatorApiClient:

    def __init__(self, restApiClient: RestApiClient) -> None:
        self.restApiClient = restApiClient

    def listIndicators(self) -> List[IndicatorSpec]:
        indicatorsListDict = self.restApiClient.doGet('/indicator/list/custom')
        result: List[IndicatorSpec] = []
        for indicatorDict in indicatorsListDict:
            result.append(IndicatorSpec.fromDict(indicatorDict))
        return result

    def getIndicatorCode(self, indicatorId: str) -> str:
        return self.restApiClient.doGet(f'/indicator/custom/{indicatorId}/code')

    def createUpdateIndicator(self,  code: str) -> IndicatorSpec:
        specDict: Dict[str, Any] = self.restApiClient.doPostCode('/indicator/custom/update', code)
        return IndicatorSpec.fromDict(specDict)
