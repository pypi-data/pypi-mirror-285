from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from numbers import Number
from typing import List, Dict, Any, cast

from investfly.models.MarketData import SecurityType
from investfly.models.MarketDataIds import FinancialField


class StandardSymbolsList(str, Enum):
    SP_100 = "SP_100"
    SP_500 = "SP_500"
    NASDAQ_100 = "NASDAQ_100"
    NASDAQ_COMPOSITE = "NASDAQ_COMPOSITE"
    RUSSELL_1000 = "RUSSELL_1000"
    DOW_JONES_INDUSTRIALS = "DOW_JONES_INDUSTRIALS"
    ETFS = "ETFS"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class CustomSecurityList:
    def __init__(self, securityType: SecurityType):
        self.securityType = securityType
        self.symbols: List[str] = []

    def addSymbol(self, symbol: str) -> None:
        self.symbols.append(symbol)

    @staticmethod
    def fromJson(json_dict: Dict[str, Any]) -> CustomSecurityList:
        securityList = CustomSecurityList(SecurityType(json_dict['securityType']))
        securityList.symbols = json_dict['symbols']
        return securityList

    def toDict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def validate(self) -> None:
        if self.securityType is None:
            raise Exception("CustomSecurityList.securityType is required")
        if len(self.symbols) == 0:
            raise Exception("CustomSecurityList.symbols: At least one symbol is required")


class SecurityUniverseType(str, Enum):
    STANDARD_LIST = "STANDARD_LIST",
    CUSTOM_LIST = "CUSTOM_LIST",
    FUNDAMENTAL_QUERY = "FUNDAMENTAL_QUERY"


class ComparisonOperator(str, Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_OR_EQUAL = ">="
    LESS_OR_EQUAL = "<="
    EQUAL_TO = "=="


@dataclass
class FinancialCondition:
    financialField: FinancialField
    operator: ComparisonOperator
    value: str | FinancialField

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> FinancialCondition:
        financialField = FinancialField[json_dict['financialField']]
        operator = ComparisonOperator[json_dict['operator']]
        valueFromJson = json_dict['value']
        allFinancialFields = [cast(FinancialField, f).name for f in FinancialField]
        if valueFromJson is allFinancialFields:
            value = FinancialField[valueFromJson]
        else:
            value = valueFromJson

        return FinancialCondition(financialField, operator, value)

    def toDict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def validate(self) -> None:
        if not isinstance(self.financialField, FinancialField):
            raise Exception("Left expression in financial query must be of type FinancialField")
        if not isinstance(self.value, FinancialField) and not isinstance(self.value, str):
            raise Exception("Right expression in financial query must of type Financial Field or string")
        if isinstance(self.value, str):
            # it must represent a number
            valueStr = self.value
            if valueStr.endswith("K") or valueStr.endswith("M") or valueStr.endswith("B"):
                valueStr = valueStr[:-1]
                if not valueStr.replace('.', '', 1).isdigit():
                    raise Exception(f"Right expression offFinancial query must be a number or Financial Field. You provided: {self.value}")



class FinancialQuery:
    def __init__(self) -> None:
        self.queryConditions: List[FinancialCondition] = []

    def addCondition(self, condition: FinancialCondition) -> None:
        self.queryConditions.append(condition)

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> FinancialQuery:
        financialQuery = FinancialQuery()
        conditionsList = json_dict['queryConditions']
        for cond in conditionsList:
            financialQuery.queryConditions.append(FinancialCondition.fromDict(cond))
        return financialQuery

    def toDict(self) -> Dict[str, Any]:
        return {'queryConditions': [q.toDict() for q in self.queryConditions]}

    def validate(self) -> None:
        if len(self.queryConditions) == 0:
            raise Exception("FinancialQuery must have at least one criteria")
        for f in self.queryConditions:
            f.validate()



@dataclass
class SecurityUniverseSelector:
    """
    This class is used to specify the set of stocks to use in trading strategy.
    You can pick one of the standard list (e.g SP100) that we provide, provide your own list with comma separated symbols list,
    or provide a query based on fundamental metrics like MarketCap, PE Ratio etc.
    """
    universeType: SecurityUniverseType
    """The approach used to specify the stocks. Depending on the universeType, one of the attribute below must be specified"""

    standardList: StandardSymbolsList | None = None
    "Standard Symbol List (i.e SP500, SP100). Required if `universeType` is set to `STANDARD_LIST`"

    customList: CustomSecurityList | None = None
    financialQuery: FinancialQuery | None = None

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> SecurityUniverseSelector:
        scopeType = SecurityUniverseType[json_dict['universeType']]
        standardList = StandardSymbolsList[json_dict['standardList']] if 'standardList' in json_dict else None
        customList = CustomSecurityList.fromJson(json_dict['customList']) if 'customList' in json_dict else None
        fundamentalQuery = FinancialQuery.fromDict(json_dict['financialQuery']) if 'financialQuery' in json_dict else None
        return SecurityUniverseSelector(scopeType, standardList, customList,  cast(FinancialQuery, fundamentalQuery))

    def toDict(self) -> Dict[str, Any]:
        jsonDict: Dict[str, Any] = {'universeType': self.universeType.value}
        if self.standardList is not None:
            jsonDict["standardList"] = self.standardList.value
        if self.customList is not None:
            jsonDict['customList'] = self.customList.toDict()
        if self.financialQuery is not None:
            jsonDict["financialQuery"] = self.financialQuery.toDict()
        return jsonDict

    @staticmethod
    def singleStock(symbol: str) -> SecurityUniverseSelector:
        scopeType = SecurityUniverseType.CUSTOM_LIST
        customList = CustomSecurityList(SecurityType.STOCK)
        customList.addSymbol(symbol)
        return SecurityUniverseSelector(scopeType, customList=customList)

    @staticmethod
    def fromStockSymbols(symbols: List[str]) -> SecurityUniverseSelector:
        scopeType = SecurityUniverseType.CUSTOM_LIST
        customList = CustomSecurityList(SecurityType.STOCK)
        customList.symbols = symbols
        return SecurityUniverseSelector(scopeType, customList=customList)

    @staticmethod
    def fromStandardList(standardListName: StandardSymbolsList) -> SecurityUniverseSelector:
        universeType = SecurityUniverseType.STANDARD_LIST
        return SecurityUniverseSelector(universeType, standardList=standardListName)

    @staticmethod
    def fromFinancialQuery(financialQuery: FinancialQuery) -> SecurityUniverseSelector:
        universeType = SecurityUniverseType.FUNDAMENTAL_QUERY
        return SecurityUniverseSelector(universeType, financialQuery=financialQuery)

    def getSecurityType(self) -> SecurityType:
        if self.universeType == SecurityUniverseType.STANDARD_LIST:
            return SecurityType.ETF if self.standardList == StandardSymbolsList.ETFS else SecurityType.STOCK
        elif self.universeType == SecurityUniverseType.CUSTOM_LIST:
            return cast(CustomSecurityList, self.customList).securityType
        else:
            return SecurityType.STOCK

    def validate(self) -> None:
        if self.universeType is None:
            raise Exception("SecurityUniverseSelector.universeType is required")
        if self.universeType == SecurityUniverseType.STANDARD_LIST:
            if self.standardList is None:
                raise Exception("SecurityUniverseSelector.standardList is required for StandardList UniverseType")
        elif self.universeType == SecurityUniverseType.CUSTOM_LIST:
            if self.customList is None:
                raise Exception("SecurityUniverseSelector.customList is required for CustomList UniverseType")
            self.customList.validate()
        elif self.universeType == SecurityUniverseType.FUNDAMENTAL_QUERY:
            if self.financialQuery is None:
                raise Exception(
                    "SecurityUniverseSelector.fundamentalQuery is required for FUNDAMENTAL_QUERY UniverseType")
            self.financialQuery.validate()

