from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import Any, Dict

from investfly.models.ModelUtils import ModelUtils


@dataclass
class DatedValue:
    """
    Data Container class to hold Time,Value for timed numeric values
    """
    date: datetime
    value: float | int

    def toJsonDict(self) -> Dict[str, Any]:
        return {
            'date': ModelUtils.formatDatetime(self.date),
            'value': self.value
        }

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> DatedValue:
        return DatedValue(ModelUtils.parseDatetime(json_dict['date']), json_dict['value'])


class TimeUnit(str, Enum):

    """
    TimeUnit Enum (MINUTES, HOURS, DAYS)
    """

    MINUTES = "MINUTES"
    HOURS = "HOURS"
    DAYS = "DAYS"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclass
class TimeDelta:
    """ TimeDelta container class similar to python timedelta """
    value: int
    unit: TimeUnit

    def toPyTimeDelta(self) -> timedelta:
        totalMinutes = self.value
        if self.unit == TimeUnit.HOURS:
            totalMinutes = totalMinutes * 60
        elif self.unit == TimeUnit.DAYS:
            totalMinutes = totalMinutes * 60 * 24

        return timedelta(minutes=totalMinutes)

    def toDict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> TimeDelta:
        return TimeDelta(json_dict['value'], TimeUnit[json_dict['unit']])


class MessageType(str, Enum):
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARN = "WARN"

@dataclass
class Message:
    type: MessageType
    message: str

    def toDict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    @staticmethod
    def fromDict(json_dict: Dict[str, Any]) -> Message:
        return Message(MessageType[json_dict['type']], json_dict['message'])




@dataclass
class Session:

    """ Class that represents logged in user session with the Investfly server """

    username: str
    clientId: str
    clientToken: str

    @staticmethod
    def fromJsonDict(json_dict: Dict[str, Any]) -> Session:
        return Session(json_dict['username'], json_dict['clientId'], json_dict['clientToken'])
