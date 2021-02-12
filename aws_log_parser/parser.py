import csv
import dataclasses
import datetime
import logging
import typing
import urllib.parse

from http import cookies

from .exceptions import UnknownHttpType
from .models import (
    LoadBalancerErrorReason,
    HttpType,
    Host,
    HttpRequest,
)

logger = logging.getLogger(__name__)


def to_http_type(value):
    for ht in HttpType:
        if ht.value == value:
            return ht
    raise UnknownHttpType(value)


def to_datetime(value):
    return datetime.datetime.fromisoformat(value.rstrip("Z")).replace(
        tzinfo=datetime.timezone.utc
    )


def to_http_request(value):
    # The url can contain spaces
    split = value.split()
    url = " ".join(split[1:-1])
    parsed = urllib.parse.urlparse(url)
    return HttpRequest(
        split[0],
        url,
        parsed.path,
        urllib.parse.parse_qs(parsed.query),
        split[-1],
    )


def to_cookie(value):
    cookie = cookies.SimpleCookie()
    cookie.load(rawdata=value)

    cookiedict = {}

    for key, morsel in cookie.items():
        cookiedict[key.replace("%20", "")] = morsel.value

    return cookiedict


def to_python(value, field):
    value = value.rstrip('"').lstrip('"')
    if field.type is datetime.datetime:
        return to_datetime(value)
    if field.type == datetime.date:
        return datetime.date.fromisoformat(value)
    if field.type == datetime.time:
        return datetime.time.fromisoformat(value)
    if field.type == typing.List[str]:
        return value.split(",")
    if value == "-":
        return None
    if field.type == LoadBalancerErrorReason:
        return getattr(LoadBalancerErrorReason, value)
    if field.type == Host:
        ip, port = value.split(":")
        return Host(ip, int(port))
    if field.type == HttpRequest:
        return to_http_request(value)
    if field.type == HttpType:
        return to_http_type(value)
    if field.name == "user_agent":
        return urllib.parse.unquote(value)
    if field.name == "uri_query":
        return urllib.parse.parse_qs(value)
    if field.name == "cookie":
        return to_cookie(value)
    return field.type(value)


def log_parser(content, log_type):
    fields = dataclasses.fields(log_type.model)
    for row in csv.reader(content, delimiter=log_type.delimiter):
        if not row[0].startswith("#"):
            yield log_type.model(
                *[to_python(value, field) for value, field in zip(row, fields)]
            )
