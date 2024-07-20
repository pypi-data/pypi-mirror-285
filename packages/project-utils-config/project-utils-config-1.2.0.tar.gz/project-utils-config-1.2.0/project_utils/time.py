import time

from datetime import datetime, timedelta


def datetime_to_str(datetime: datetime = datetime.now(), format="%Y-%m-%d %H:%M:%S") -> str:
    return datetime.strftime(format)


def timestamp_to_str(timestamp: float = time.time(), format: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime_to_str(datetime.fromtimestamp(timestamp), format)


def datetime_to_timestamp(datetime: datetime = datetime.now()) -> float:
    return datetime.timestamp()


def str_to_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(date_str, format)


def str_to_timestamp(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> float:
    date_attr: datetime = str_to_datetime(date_str, format)
    return date_attr.timestamp()


def timestamp_to_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp)


def compute_year(year: int = 0, date: datetime = datetime.now()) -> datetime:
    year: int = date.year - year
    month: int = date.month
    day: int = date.day
    return datetime(year, month, day)


def compute_month(month: int = 0, date: datetime = datetime.now()) -> datetime:
    year: int = date.year
    month = date.month - month
    day = date.day
    return datetime(year, month, day)


def compute_week(week: int = 0, date: datetime = datetime.now()) -> datetime:
    return date + timedelta(weeks=week)


def compute_day(day: int = 0, date: datetime = datetime.now()) -> datetime:
    return date + timedelta(days=day)


def compute_hour(hour: int = 0, date: datetime = datetime.now()) -> datetime:
    return date + timedelta(hours=hour)


def compute_minute(minute: int = 0, date: datetime = datetime.now()) -> datetime:
    return date + timedelta(minutes=minute)


def compute_second(second: int = 0, date: datetime = datetime.now()) -> datetime:
    return date + timedelta(seconds=second)


if __name__ == '__main__':
    print(len(timestamp_to_str(is_date=True)))
