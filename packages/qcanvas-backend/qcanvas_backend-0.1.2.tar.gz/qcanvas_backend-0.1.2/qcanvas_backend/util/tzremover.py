from datetime import datetime


def strip_tz(date: datetime) -> datetime:
    return date.replace(tzinfo=None)
