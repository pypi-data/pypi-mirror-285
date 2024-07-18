# This is a self-documenting starter template to define custom indicators in Python Programming Language

# Following two imports are required
from investfly.models import *
from investfly.utils import *

# Import basic types, they aren't required but recommended
from typing import Any, List, Dict

# Following numeric analysis imports are allowed
import math
import statistics
import numpy as np
import talib
import pandas

# ! WARN ! Imports other than listed above are disallowed and won't pass validation

# Create a class that extends Indicator. The class name becomes the "IndicatorId", which must be globally unique
class SMAHeikin_CHANGE_ME(Indicator):

    # At minimum, you must implement two methods (1) getIndicatorSpec and (2) shown below.
    def getIndicatorSpec(self) -> IndicatorSpec:
        # In this method, you must construct and return IndicatorSpec object that specifies
        # indicator name, description and any parameters it needs.

        # This information is used by Investfly UI to display information about this indicator in the expression builder

        indicator = IndicatorSpec("[Change Me]: SMA Heikin Ashi")
        indicator.description = "[ChangeMe]: SMA based on Heikin Ashi Candles"

        # This indicates that the indicator value will have the same unit as stock price and can be plotted
        # in the same y-axis as stock price as overlay. If the indicator results in a unit-less number like
        # ADX, you will set it to IndicatorValueType.NUMBER. Other possible values are PERCENT, RATIO, BOOLEAN
        indicator.valueType = IndicatorValueType.PRICE

        # Specify indicator parameters. For each parameter, you must provide IndicatorParamSpec with
        # paramType: one of [ParamType.INTEGER, ParamType.FLOAT, ParamType.STRING, ParamType.BOOLEAN]
        # The remaining properties of ParamSpec are optional
        # required: [True|False], defaults to True
        # options:List[Any]:  List of valid values . This will make the parameter input widget appear as a dropdown
        indicator.addParam("period", IndicatorParamSpec(paramType=ParamType.INTEGER, options=IndicatorParamSpec.PERIOD_VALUES))
        return indicator

    def computeSeries(self, params: Dict[str, Any], bars: List[Bar]) -> List[DatedValue]:
        # In this method, you compute indicator values for provided parameter values and given data (bars in this case)
        # For use in strategy, only the latest indicator value is required, but you must compute full series of historical
        # values so that this indicator can be plotted in the chart and we can run also backtest strategy when this
        # indicator is used in trading strategy

        # In this template, we will calculate SMA, but using Heikin Ashi candles
        heikinCandles = CommonUtils.toHeikinAshi(bars)

        dates, close = CommonUtils.extractCloseSeries(heikinCandles)
        sma_period = params['period']

        # talib requires numpy.array instead of Python arrays, so wrap the close array into np.array
        smaSeries = talib.SMA(np.array(close), timeperiod=sma_period)

        # Converts the returned numpy.array into List[DatedValue]
        return CommonUtils.createListOfDatedValue(dates, smaSeries)


    # +++++++ The following methods are optional ******

    def dataCountToComputeCurrentValue(self, params: Dict[str, Any]) -> int | None:
        # As stated above, we only need the latest indicator value while evaluating strategy in real-time.
        # Here, you return how many input data points are needed to compute just the latest indicator value.
        # For e.g, to compute SMA(5), you need 5 data points. The return value from this method determines
        # the length of input data that is passed to computeSeries method above when this indicator evaluates
        # in real-time execution mode. This speeds up computation significantly by avoiding un-necessary computation
        # The base class (Indicator) contains implementation of this method that tries to make the best guess,
        # but it is highly recommended to override this method
        sma_period = params['period']
        return sma_period

    def getDataSourceType(self) -> DataSource:
        # Currenly, only bars are supported. But in the future, we will support defining indicators based on alternate data sources
        # such as news feed etc. The default is DataSource.BARS
        return DataSource.BARS
