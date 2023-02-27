import datetime
import json
import typing

from .conftest import parse_entry

from aws_log_parser.models import (
    LogType,
    WafLogEntry,
)

from pprint import pprint


def test_waf_entry(waf_entry):
    waf_entry = typing.cast(
        WafLogEntry, parse_entry([json.loads(waf_entry.read())], LogType.WAF)
    )
    pprint(waf_entry)
    pprint(waf_entry.schema())
    assert isinstance(waf_entry.timestamp, datetime.datetime) is True
