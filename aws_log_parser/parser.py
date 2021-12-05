import datetime
import logging
import typing
import urllib.parse

from http import cookies

from .exceptions import UnknownHttpType
from .models import (
    HttpType,
    Host,
    HttpRequest,
    LoadBalancerErrorReason,
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
    return {urllib.parse.unquote(key): morsel.value for key, morsel in cookie.items()}


def to_python(value, field):
    value = value.strip('"')

    origin = typing.get_origin(field.type)
    field_type = (
        typing.get_args(field.type)[0]  # XXX: only supports Optional types
        if origin == typing.Union
        else field.type
    )

    if field_type is datetime.datetime:
        return to_datetime(value)
    if field_type == datetime.date:
        return datetime.date.fromisoformat(value)
    if field_type == datetime.time:
        return datetime.time.fromisoformat(value)
    if field_type == typing.List[str]:
        return value.split(",")
    if value == "-":
        return None
    if field_type == LoadBalancerErrorReason:
        return getattr(LoadBalancerErrorReason, value)
    if field_type == Host:
        ip, port = value.split(":")
        return Host(ip, int(port))
    if field_type == HttpRequest:
        return to_http_request(value)
    if field_type == HttpType:
        return to_http_type(value)
    if field.name == "user_agent":
        return urllib.parse.unquote(value)
    if field.name == "uri_query":
        return urllib.parse.parse_qs(value)
    if field.name == "cookie":
        return to_cookie(value)
    return field_type(value)
