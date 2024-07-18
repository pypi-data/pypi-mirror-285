import math
from datetime import datetime
from typing import List, Tuple, Any

import numpy
import pandas as pd

from investfly.models import DatedValue, Bar


def createPandasDf(bars: List[Bar]) -> pd.DataFrame:
    df = pd.DataFrame(bars)
    df.set_index("date", inplace=True)
    return df

def extractCloseSeries(bars: List[Bar]) -> Tuple[List[datetime], List[float]]:
    dates: List[datetime] = [b['date'] for b in bars]
    closeSeries: List[float] = [b['close'] for b in bars]
    return dates, closeSeries

def extractOHLCSeries(bars: List[Bar]) -> Tuple[List[datetime], List[float], List[float], List[float], List[float]]:
    dates: List[datetime] = [b['date'] for b in bars]
    openSeries: List[float] = [b['open'] for b in bars]
    highSeries: List[float] = [b['high'] for b in bars]
    lowSeries: List[float] = [b['low'] for b in bars]
    closeSeries: List[float] = [b['close'] for b in bars]
    return dates, openSeries, highSeries, lowSeries, closeSeries


def pandasSeriesToList(series: pd.Series) -> List[DatedValue]:
    records = series.to_dict() # float64 is auto-converted to float by to_dict
    result: List[DatedValue] = []
    for key in records:
        date = key.to_pydatetime()  # type: ignore
        val = records[key]
        if not math.isnan(val):
            result.append(DatedValue(date, val))
    return result

def createListOfDatedValue(dates: List[datetime], values: numpy.ndarray[Any, numpy.dtype[numpy.float64]]):
    result: List[DatedValue] = []
    for i in range(len(dates)):
        date: datetime = dates[i]
        val = values[i]
        if not numpy.isnan(val):
            result.append(DatedValue(date, val.item()))
    return result

def floatListToDatedValueList(dates: List[datetime], values: List[float]):
    result: List[DatedValue] = []
    for i in range(len(dates)):
        date: datetime = dates[i]
        val = values[i]
        result.append(DatedValue(date, val))
    return result

def toHeikinAshi(bars: List[Bar]) -> List[Bar]:
    heiken: List[Bar] = []
    for i in range(len(bars)):
        b = bars[i]
        h = Bar()
        h['symbol'] = b['symbol']
        h['date'] = b['date']
        h['barinterval'] = b['barinterval']
        h['volume'] = b['volume']

        h['close'] = (b['open'] + b['high'] + b['low'] + b['close']) / 4

        if i == 0:
            h['open'] = (b['open'] + b['close'])/2
        else:
            h['open'] = (bars[i-1]['open'] + bars[i-1]['close'])/2

        h['high'] = max(b['high'], h['open'], h['close'])
        h['low'] = min(b['low'], h['open'], h['close'])

        heiken.append(h)

    return heiken
