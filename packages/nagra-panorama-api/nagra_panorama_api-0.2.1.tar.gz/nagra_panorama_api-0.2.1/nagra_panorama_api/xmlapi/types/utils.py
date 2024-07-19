import logging
from datetime import datetime

from pydantic.functional_validators import PlainValidator
from typing_extensions import Annotated, TypeAliasType

from nagra_panorama_api.utils import (
    first,
)

DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"


def parse_datetime(d):
    try:
        if d is None:
            return d
        return datetime.strptime(d, DATETIME_FORMAT)
    except Exception as e:
        logging.debug(e)
        logging.debug(f"Failed to parse {d} as datetime")
    return d


def parse_time(d):
    return datetime.strptime(d, TIME_FORMAT).time()


# https://docs.pydantic.dev/latest/concepts/types/#custom-types
# JobProgress = TypeAliasType('JobProgress', PlainValidator(parse_progress))
Datetime = TypeAliasType(
    "Datetime", Annotated[datetime, PlainValidator(parse_datetime)]
)


def single_xpath(xml, xpath, parser=None, default=None):
    try:
        res = xml.xpath(xpath)
        res = first(res, None)
    except Exception:
        return default
    if res is None:
        return default
    if not isinstance(res, str):
        res = res.text
    if parser:
        res = parser(res)
    return res


pd = parse_datetime
sx = single_xpath


def mksx(xml):
    def single_xpath(xpath, parser=None, default=None):
        res = sx(xml, xpath, parser=parser, default=default)
        logging.debug(res)
        return res

    return single_xpath
