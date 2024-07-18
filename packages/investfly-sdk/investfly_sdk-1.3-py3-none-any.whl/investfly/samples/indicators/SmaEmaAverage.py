from typing import Any, List, Dict

import numpy as np
import talib

from investfly.models import *
from investfly.utils import *

# This sample show how you can use pandas_ta module at https://github.com/twopirllc/pandas-ta
# to compute over 100 technical indicators
# This indicator computes average of SMA and EMA for given period

class SmaEmaAverage(Indicator):

    # To implement a price-based indicator (i.e indicator that uses price bars [open,high,low,close,volume]) in
    # computation you extend from PriceBasedIndicator and implement  methods shown below

    def getIndicatorSpec(self) -> IndicatorSpec:
        # In this method, you must construct and return IndicatorDefinition object that spefies
        # indicator name, description and any parameters it needs. BarSize parameter is automatically
        # added from the parent class
        indicator = IndicatorSpec("SMA EMA Average")
        indicator.addParam('period', IndicatorParamSpec(ParamType.INTEGER, True, 5, IndicatorParamSpec.PERIOD_VALUES))
        return indicator

    def getDataSourceType(self) -> DataSource:
        return DataSource.BARS


    def computeSeries(self, params: Dict[str, Any], bars: List[Bar]) -> List[DatedValue]:
        # Load the bars into Pandas dataframe
        dates, close = CommonUtils.extractCloseSeries(bars)
        # Get supplied period
        period = params['period']
        # Call pandas_ta module to compute sma and ema
        # see https://github.com/twopirllc/pandas-ta
        smaSeries = talib.SMA(np.array(close), timeperiod=period)
        emaSeries = talib.EMA(np.array(close), timeperiod=period)
        avgSeries = (smaSeries + emaSeries) / 2
        return CommonUtils.createListOfDatedValue(dates, avgSeries)
