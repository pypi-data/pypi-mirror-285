from datetime import datetime
import pytz


class ModelUtils:

    # In Java, using Date includes timezone offset in JSON whereas using LocalDateTime does not

    est_tz = pytz.timezone('America/New_York')

    @staticmethod
    def localizeDateTime(dt: datetime) -> datetime:
        return ModelUtils.est_tz.localize(dt)


    @staticmethod
    def parseDatetime(date_str: str) -> datetime:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
        dt = dt.astimezone(ModelUtils.est_tz)
        return dt

    @staticmethod
    def formatDatetime(dt: datetime) -> str:
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')

    @staticmethod
    def parseZonedDatetime(date_str: str) -> datetime:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        dt = dt.astimezone(ModelUtils.est_tz)
        return dt

    @staticmethod
    def formatZonedDatetime(dt: datetime) -> str:
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')