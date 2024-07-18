from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List


from investfly.models.CommonModels import TimeDelta
from investfly.models.MarketData import Security
from investfly.models.ModelUtils import ModelUtils
from investfly.models.PortfolioModels import PositionType, Portfolio, TradeOrder, PortfolioPerformance
from investfly.models.SecurityFilterModels import DataParam


def DataParams(params: Dict[str, Dict[str, Any]]):
    def decorator_func(func):
        def wrapper_func(*args, **kwargs):
            return func(*args, **kwargs)

        dataParams = {}
        for key in params.keys():
            paramDict = params[key]
            dataParam = DataParam.fromDict(paramDict)
            dataParams[key] = dataParam
        return wrapper_func, dataParams

    return decorator_func


class ScheduleInterval(str, Enum):
    DAILY_AFTER_MARKET_OPEN = "DAILY_AFTER_MARKET_OPEN"
    DAILY_AFTER_MARKET_CLOSE = "DAILY_AFTER_MARKET_CLOSE"
    HOURLY_DURING_MARKET_OPEN = "HOURLY_DURING_MARKET_OPEN"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


def Schedule(param: ScheduleInterval | None):
    def decorator_func(func):
        def wrapper_func(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper_func, param

    return decorator_func


@dataclass
class TradeSignal:
    security: Security
    position: PositionType
    strength: int = 1
    data: Dict[str, Any] | None = None  # Any other data besides strength that could be useful to generate TradeOrder


@dataclass
class StandardCloseCriteria:
    targetProfit: float | None  # specify in scaled [0 - 100 range]
    stopLoss: float | None  # specify as negative
    trailingStop: float| None # specify as negative
    timeOut: TimeDelta | None

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> StandardCloseCriteria:
        return StandardCloseCriteria(
            json_dict.get('targetProfit'),
            json_dict.get('stopLoss'),
            json_dict.get('trailingStop'),
            TimeDelta.fromDict(json_dict['timeout']) if 'timeout' in json_dict else None
        )

    def toDict(self) -> Dict[str, Any]:
        jsonDict = self.__dict__.copy()
        if self.timeOut is not None:
            jsonDict['timeout'] = self.timeOut.toDict()
        return jsonDict



class PortfolioSecurityAllocator(ABC):

    @abstractmethod
    def allocatePortfolio(self, portfolio: Portfolio, tradeSignals: List[TradeSignal]) -> List[TradeOrder]:
        pass


class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

@dataclass
class DeploymentLog:
    date: datetime
    level: LogLevel
    message: str

    @staticmethod
    def info(message: str) -> DeploymentLog:
        return DeploymentLog(datetime.now(), LogLevel.INFO, message)

    @staticmethod
    def warn(message: str) -> DeploymentLog:
        return DeploymentLog(datetime.now(), LogLevel.WARN, message)

    @staticmethod
    def error(message: str) -> DeploymentLog:
        return DeploymentLog(datetime.now(), LogLevel.ERROR, message)

    def toDict(self) -> Dict[str, Any]:
        dict = self.__dict__.copy()
        dict['date'] = ModelUtils.formatDatetime(self.date)
        return dict

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> DeploymentLog:
        return DeploymentLog(ModelUtils.parseDatetime(json_dict['date']), LogLevel(json_dict['level']), json_dict['message'])

class StandardOrCustom(str, Enum):
    STANDARD = "STANDARD"
    CUSTOM = "CUSTOM"

@dataclass
class TradingStrategyModel:
    strategyName: str
    strategyId: int | None = None
    pythonCode: str | None = None
    strategyDesc: str | None = None

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> TradingStrategyModel:
        strategyId = json_dict['strategyId']
        strategyName = json_dict['strategyName']
        pythonCode = json_dict['pythonCode']
        strategyDesc = json_dict.get('strategyDesc')
        return TradingStrategyModel(strategyId=strategyId, strategyName=strategyName, pythonCode=pythonCode, strategyDesc=strategyDesc)

    def toDict(self) -> Dict[str, Any]:
        dict = self.__dict__.copy()
        return dict


class BacktestStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED",
    QUEUED = "QUEUED",
    INITIALIZING = "INITIALIZING",
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

@dataclass
class BacktestResultStatus:
    jobStatus: BacktestStatus
    percentComplete: int

    def toDict(self) -> Dict[str, Any]:
        dict = self.__dict__.copy()
        return dict

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> BacktestResultStatus:
        status = BacktestStatus[json_dict['jobStatus']]
        percentComplete = json_dict['percentComplete']
        return  BacktestResultStatus(status, percentComplete)

@dataclass
class BacktestResult:
    status: BacktestResultStatus
    performance: PortfolioPerformance
    def toDict(self) -> Dict[str, Any]:
        dict = self.__dict__.copy()
        dict['performance'] = self.performance.toDict()
        return dict

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> BacktestResult:
        status = BacktestResultStatus.fromDict(json_dict['status'])
        performance = PortfolioPerformance.fromDict(json_dict['performance'])
        return BacktestResult(status, performance)