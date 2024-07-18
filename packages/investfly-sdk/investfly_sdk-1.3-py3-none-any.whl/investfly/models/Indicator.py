from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List,  ClassVar

from investfly.models.CommonModels import DatedValue
from investfly.models.MarketData import BarInterval
from investfly.models.SecurityFilterModels import DataSource, DataParam


class ParamType(str, Enum):

    """ Indicator Param Type """

    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    BARINTERVAL = 'BARINTERVAL'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclass
class IndicatorParamSpec:

    """ Class that represents Indicator Parameter Specification """

    paramType: ParamType
    """ Parameter Type (INTEGER, FLOAT, BOOLEAN, STRING, BARINTERVAL) """

    required: bool = True
    """ Whether this parameter is required or optional"""

    # The default value here is just a "hint" to the UI to auto-fill indicator value with reasonable default
    defaultValue: Any | None = None
    """ The default value for the parameter to auto-populate mainly in UI """

    options: List[Any] | None = None
    """ Valid value options (if any). If specified, then in the UI, this parameter renders as a dropdown select list.
    If left as None, parameter renders and freeform input text field. """

    PERIOD_VALUES: ClassVar[List[int]] = [2, 3, 4, 5, 8, 9, 10, 12, 14, 15, 20, 26, 30, 40, 50, 60, 70, 80, 90, 100, 120, 130, 140, 150, 180, 200, 250, 300]

    def toDict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        return d

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> IndicatorParamSpec:
        paramType = ParamType[json_dict['paramType']]
        required = json_dict['required']
        defaultValue = json_dict.get('defaultValue')
        options = json_dict.get('options')
        return IndicatorParamSpec(paramType, required, defaultValue, options)


class IndicatorValueType(str, Enum):
    """
    Indicator ValueType can possibly used by Investfly to validate expression and optimize experience for users
    For e.g, all Indicators of same valueType can be plotted in the same y-axis
    """

    PRICE = "PRICE"

    # Values that ranges from 0-100
    PERCENT = "PERCENT"

    # Values that ranges from 0-1
    RATIO = "RATIO"

    # The value must be 0 or 1
    BOOLEAN = "BOOLEAN"

    # For arbitrary numeric value, use NUMBER, which is also the default
    NUMBER = "NUMBER"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

# IndicatorDefinition represents indicator used in Investfly. Each indicator implementation must provide
# IndicatorDefinition, that specifies its name, description, required parameters and what type of value
# it returns.

class IndicatorSpec:

    def __init__(self, name: str) -> None:
        # indicatorId is automatically set to clazz name of the indicator implementation
        self.indicatorId: str

        self.name: str = name

        # Description is defaulted to name for simplicity but can be set properly after instantiation
        self.description: str = name

        self.valueType: IndicatorValueType = IndicatorValueType.NUMBER
        self.params: Dict[str, IndicatorParamSpec] = {}

    def addParam(self, paramName: str, paramSpec: IndicatorParamSpec) -> None:
        self.params[paramName] = paramSpec

    def toJsonDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        # IndicatorParamSpec.toDict() must be called
        paramsDict = {}
        for paramName in self.params.keys():
            paramsDict[paramName] = self.params[paramName].toDict()
        jsonDict['params'] = paramsDict
        return jsonDict

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> IndicatorSpec:
        name = json_dict['name']
        indicatorSpec: IndicatorSpec = IndicatorSpec(name)
        indicatorSpec.indicatorId = json_dict['indicatorId']
        indicatorSpec.description = json_dict['description']
        indicatorSpec.valueType = IndicatorValueType[json_dict['valueType']]
        for key, value in json_dict['params'].items():
            indicatorSpec.params[key] = IndicatorParamSpec.fromDict(value)
        return indicatorSpec

    def __str__(self):
        return str(self.__dict__)


class Indicator(ABC):
    """
    The primary class to implement a custom Indicator. A Custom Indicator is like standard indicator (e.g SMA, RSI)
    and can be used in any place that standard indicator can be used (e.g screener, charts, strategy etc)
    Investfly comes with a set of standard indicators. If you find that the indicator you want is not supported
    or you can a small variation (e.g SMA but with using Heikin Ashi Candles), then you can use this function
    """

    @abstractmethod
    def getIndicatorSpec(self) -> IndicatorSpec:
        """
        Return IndicatorSpec with name, description, required params, and valuetype
        See IndicatorSpec abstract class for more details
        :return:  `IndicatorSpec`
        """

        pass

    def getDataSourceType(self) -> DataSource:
        """
        Return the DataSource that this indicator is based on. Possible values are:
        DataSource.BARS, DataSource.QUOTE, DataSource.NEWS, DataSource.FINANCIAL
        :return: `investfly.models.SecurityFilterModels.DataSource`
        """

        return DataSource.BARS

    @abstractmethod
    def computeSeries(self, params: Dict[str, Any], data: List[Any]) -> List[DatedValue]:
        """
        Compute indicator series based on provided input timed data series and parameter values.
        This function must return List of indicator values instead of only the most recent single value because indicator
        series is required to plot in the price chart and also to use in backtest
        The timestamps in the `investfly.models.CommonModels.DatedValue` must correspond to timestamps in input data
        The length of input data depends on context (e.g is this indicator being evaluated for backtest or screener?)
        and  `dataCountToComputeCurrentValue` function below

        :param params: User supplied indicator parameter values. The keys match the keys from `IndicatorSpec.params`
        :param data: List of timed data values as specified in `Indicator.getDataSourceType`.
        :return: List of `investfly.models.CommonModels.DatedValue` representing indicator values for each timeunit
        """

        pass

    def dataCountToComputeCurrentValue(self, params: Dict[str, Any]) -> int | None:
        """
        When this indicator is used in screener and trading strategy when is evaluated in real-time, only
        the "current" value of the indicator is required. The historical values are NOT required. Therefore,
        when the system calls `computeSeries` above with all available data (e.g 10 years of historical bars),
        then it is un-necessarily slow and wasteful. This function is used to control the size of input data
        that will be passed to `computeSeries` method above.

        The default implementation tries to make the best guess, but override as needed

        :param params: User supplied input parameter  values
        :return: integer representing how many input data points are required to compute the 'current' indicator value.
        For e.g, if this was SMA indicator with period=5, then you should return 5
        """
        total = 0
        for key, value in params.items():
            if isinstance(value, int) and key != DataParam.COUNT:
                total += value
        return max(total, 1)

    def validateParams(self, paramVals:  Dict[str, Any]):
        spec: IndicatorSpec = self.getIndicatorSpec()
        for paramName, paramSpec in spec.params.items():
            paramVal: Any = paramVals.get(paramName)
            expectedParamType = paramSpec.paramType

            if paramVal is not None:
                if expectedParamType == ParamType.INTEGER and not isinstance(paramVal, int):
                    raise Exception(f"Param {paramName} must be of type int. You provided: {paramVal}")
                if expectedParamType == ParamType.FLOAT and not isinstance(paramVal, float) and isinstance(paramVal,int):
                    raise Exception(f"Param {paramName} must be of type float. You provided: {paramVal}")
                if expectedParamType == ParamType.STRING and not isinstance(paramVal, str):
                    raise Exception(f"Param {paramName} must be of type string. You provided: {paramVal}")
                if expectedParamType == ParamType.BOOLEAN and not isinstance(paramVal, bool):
                    raise Exception(f"Param {paramName} must be of type boolean. You provided: {paramVal}")
                if expectedParamType == ParamType.BOOLEAN and not isinstance(paramVal, bool):
                    raise Exception(f"Param {paramName} must be of type boolean. You provided: {paramVal}")
                if expectedParamType == ParamType.BARINTERVAL and not isinstance(paramVal, BarInterval):
                    raise Exception(f"Param {paramName} must be of type BarInterval. You provided: {paramVal}")

                if paramSpec.options is not None:
                    if paramVal not in paramSpec.options:
                        raise Exception(f"Param {paramName} provided value {paramVal} is not one of the allowed value")


    def addStandardParamsToDef(self, indicatorDef: IndicatorSpec):
        # Note that setting default values for optional params impact alias/key generation for indicator instances (e.g SMA_5_1MIN_1)
        # Hence, its better to leave them as None
        indicatorDef.params[DataParam.COUNT] = IndicatorParamSpec(ParamType.INTEGER, False, None)
        indicatorDef.params[DataParam.LOOKBACK] = IndicatorParamSpec(ParamType.INTEGER, False, None, [1,2,3,4,5,6,7,8,9,10])
        indicatorDef.params[DataParam.SECURITY] = IndicatorParamSpec(ParamType.STRING, False)

        # Add datasource dependent parameters
        dataSource = self.getDataSourceType()
        if dataSource == DataSource.BARS:
            indicatorDef.params[DataParam.BARINTERVAL] = IndicatorParamSpec(ParamType.BARINTERVAL, True, BarInterval.ONE_MINUTE,   [v for v in BarInterval])
        elif dataSource == DataSource.FINANCIAL or dataSource == DataSource.QUOTE:
            # Its optional because in the absense of field, indicator.computeSeries() will be passed full FinancialDict
            indicatorDef.params[DataParam.FIELD] = IndicatorParamSpec(ParamType.STRING, False)


