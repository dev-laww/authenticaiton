import datetime

import arrow


def get_current_utc_datetime() -> datetime.datetime:
    """
    Get the current UTC datetime with timezone awareness
    """
    return arrow.utcnow().datetime


__all__ = ["get_current_utc_datetime"]
