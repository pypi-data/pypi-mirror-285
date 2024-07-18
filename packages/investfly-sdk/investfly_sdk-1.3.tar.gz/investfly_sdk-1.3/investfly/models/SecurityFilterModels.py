from __future__ import annotations

import numbers
from enum import Enum
from typing import Dict, Any, cast

from investfly.models.MarketData import BarInterval
from investfly.models.MarketDataIds import QuoteField, FinancialField


class DataSource(str, Enum):
    BARS = "BARS"
    FINANCIAL = "FINANCIAL"
    QUOTE = "QUOTE"
    NEWS = "NEWS"


class DataType(str, Enum):
    BARS = "BARS"
    FINANCIAL = "FINANCIAL"
    QUOTE = "QUOTE"
    NEWS = "NEWS"

    INDICATOR = "INDICATOR"
    CONST = "CONST"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ConstUnit(str, Enum):
    K = "K"
    M = "M"
    B = "B"


class DataParam(Dict[str, Any]):
    SECURITY = "security"
    FIELD = "field"
    INDICATOR = "indicator"
    DATATYPE = "datatype"
    VALUE = "value"
    UNIT = "unit"
    BARINTERVAL = "barinterval"
    LOOKBACK = "lookback"
    COUNT = "count"

    def setDataType(self, dataType: DataType) -> None:
        self[DataParam.DATATYPE] = dataType

    def getDataType(self) -> DataType:
        return cast(DataType, self.get(DataParam.DATATYPE))

    def getIndicatorId(self) -> str:
        return cast(str, self.get(DataParam.INDICATOR))

    def getBarInterval(self) -> BarInterval|None:
        return self.get(DataParam.BARINTERVAL)

    def getQuoteField(self) -> QuoteField | None:
        return self.get(DataParam.FIELD)

    def getFinancialField(self) -> FinancialField | None:
        return self.get(DataParam.FIELD)

    def getCount(self) -> int | None:
        return self.get(DataParam.COUNT)

    def getLookback(self) -> int | None:
        return self.get(DataParam.LOOKBACK)

    def getConstValue(self) -> int | float:
        val = cast(int|float, self.get(DataParam.VALUE))
        unit: ConstUnit|None = self.get(DataParam.UNIT)
        if unit is None:
            return val
        elif unit == ConstUnit.K:
            return val * 1000
        elif unit == ConstUnit.M:
            return val * 1000000
        elif unit == ConstUnit.B:
            return val * 1000000000
        else:
            raise Exception(f"Unknown unit {unit}")

    def getSecurity(self) -> str | None:
        return self.get(DataParam.SECURITY)

    def validate(self) -> None:
        dataType: DataType|None = self.get(DataParam.DATATYPE)
        if dataType is None:
            raise Exception("'datatype' attribute is required for all data parameters")
        if not isinstance(dataType, DataType):
            raise Exception(f"'datatype' must of of type Enum DataType")

        if dataType == DataType.CONST:
            value: numbers.Number|None = self.get(DataParam.VALUE)
            unit: ConstUnit|None = self.get(DataParam.UNIT)
            if value is None:
                raise Exception("'value' attribute is required for CONST datatype")
            if not isinstance(value, numbers.Number):
                raise Exception("const value must be a number")
            if unit is not None and not isinstance(unit, ConstUnit):
                raise Exception("const unit must be of type ConstUnit")

        elif dataType == DataType.QUOTE:
            quoteField: QuoteField|None = self.get(DataParam.FIELD)
            if quoteField is not None:
                if not isinstance(quoteField, QuoteField):
                    raise Exception("'field' attribute for 'Quote' datatype must be QuoteField")

        elif dataType == DataType.FINANCIAL:
            financialField: FinancialField|None = self.get(DataParam.FIELD)
            if financialField is not None:
                if not isinstance(financialField, FinancialField):
                    raise Exception("'field' attribute for 'Quote' datatype must be FinancialField")

        elif dataType == DataType.INDICATOR:
            indicatorId: str|None = self.getIndicatorId()
            if indicatorId is None:
                raise Exception("'indicator' attribute is required for Indicator datatype")

        elif dataType == DataType.BARS:
            barPrice = self.get("price")
            if barPrice is not None:
                if barPrice not in ["open", "high", "low", "close", "volume"]:
                    raise Exception("'price' attribute in BARS type must be on of [open, high, low, close, volume]")

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> DataParam:
        dataParam = DataParam()
        dataType: DataType = DataType[cast(str, json_dict.get(DataParam.DATATYPE))]
        dataParam.setDataType(dataType)

        for key in json_dict.keys():
            value = json_dict[key]
            if key == DataParam.DATATYPE:
                continue
            elif key == DataParam.BARINTERVAL:
                dataParam[key] = BarInterval[value]
            elif key == DataParam.FIELD:
                if dataType == DataType.QUOTE:
                    dataParam[key] = QuoteField[value]
                elif dataType == DataType.FINANCIAL:
                    dataParam[key] = FinancialField[value]
                else:
                    dataParam[key] = value
            elif key == DataParam.INDICATOR:
                # Since indicator can also be custom indicator, it cant be converted to StandardIndicatorId enum
                dataParam[key] = value
            elif key == DataParam.VALUE:
                # json.loads should already have converted to int or float based on the value
                dataParam[key] = value
            elif key == DataParam.UNIT:
                dataParam[key] = ConstUnit[value]
            else:
                dataParam[key] = value
        return dataParam

    def clone(self) -> DataParam:
        dataParam: DataParam = DataParam()
        for key in self.keys():
            dataParam[key] = self.get(key)
        return dataParam
