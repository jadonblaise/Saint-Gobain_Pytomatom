import datetime
import logging

import pandas as pd


log = logging.getLogger("django.plans")


def timestamp_to_datetime(d: dict, *, key: str, pattern: str = "%Y-%m-%dT%H:%M:%S") -> dict:
    """
    Convert datetime string to datetime (in given pattern format).
    Fallsback to None for invalid transformations.
    """
    value: datetime.date | None = None
    candidate = d[key]
    if pd.isnull(candidate):
        log.warning(f"pd.isnull {candidate=} {d=}")
    else:
        try:
            value = datetime.datetime.strptime(candidate, pattern).date()
        except TypeError as exc:
            log.debug(f"Can not convert {type(candidate)=} to date. {exc=}")
            value = None
        except ValueError as exc:
            log.debug(f"Can not convert {candidate=} to date. {exc=}")
            value = None

    d[key] = value
    return d


def translate(entry: dict, translation: dict) -> dict:
    """
    Translates keys in entries.
        translation: {old: new}

    Be aware of using different types to rename ( "22" (str) is not 22 (int) )
    """
    return {translation.get(key): value for key, value in entry.items() if key in translation.keys()}
