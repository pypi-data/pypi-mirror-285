import datetime

import cherrypy

from dateutil.parser import parse as dateutil_parse
from pytz import timezone
from typing import Iterable, Dict


utc = timezone("UTC")
eastern = timezone("US/Eastern")


def default_timestamp() -> datetime.datetime:
    return datetime.datetime(year=1970, month=1, day=1, second=1)


def format_timestamp(timestamp: datetime.datetime):
    timestamp.isoformat()


def parse_timestamp(timestamp: str) -> datetime.datetime:
    naive_datetime = dateutil_parse(timestamp.split("[")[0])
    return as_utc(naive_datetime)


def as_utc(timestamp: datetime.datetime):
    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        return utc.localize(timestamp)
    else:
        return timestamp.astimezone(utc)


def as_eastern(timestamp: datetime.datetime):
    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        return eastern.localize(timestamp)
    else:
        return timestamp.astimezone(eastern)


def convert_dictionary_keys(dictionary: Dict, keys: Iterable[str]):
    for key in keys:
        if not dictionary[key]:
            cherrypy.log("Converting timestamp for key {0} but value is empty, setting it to None".format(key))
            dictionary[key] = None
            continue

        dictionary[key] = parse_timestamp(dictionary[key])

    return dictionary
