import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union

from dateutil import parser


def today() -> datetime:
    dt = datetime.utcnow()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def to_datetime(str_date: str) -> datetime:
    dt = parser.parse(str_date)
    return dt.replace(tzinfo=timezone.utc)


def to_short_str_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def to_utc_isostring(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat()


def timestamp_now() -> int:
    return int(time.time())


def from_timestamp(timestamp: Union[int, Decimal]) -> datetime:
    dt = datetime.utcfromtimestamp(timestamp)
    return dt.replace(tzinfo=timezone.utc)


def to_timestamp(dt: datetime) -> int:
    return int(datetime.timestamp(dt))
