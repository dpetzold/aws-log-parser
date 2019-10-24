import csv
import dataclasses
import datetime
import typing
import user_agents
import urllib

from user_agents.parsers import UserAgent

from .models import (
    Host,
    HttpRequest,
    LoadBalancerErrorReason,
)


def to_list(value):
    return value.split(',')


def to_host(value):
    ip, port = value.split(':')
    return Host(ip, int(port))


def to_datetime(value):
    return datetime.datetime.fromisoformat(
        value.rstrip('Z')
    ).replace(tzinfo=datetime.timezone.utc)


def to_date(value):
    return datetime.date.fromisoformat(value)


def to_time(value):
    return datetime.time.fromisoformat(value)


def to_loadbalancer_error_reason(value):
    return getattr(LoadBalancerErrorReason, value)


def to_user_agent(value):
    return user_agents.parse(value)


def to_http_request(value):
    # The url can contain spaces
    split = value.split()
    url = ' '.join(split[1:-1])
    parsed = urllib.parse.urlparse(url)
    return HttpRequest(
        split[0],
        url,
        urllib.parse.parse_qs(parsed.query),
        split[-1],
    )


TYPE_MAPPINGS = {
    datetime.date: to_date,
    datetime.time: to_time,
    datetime.datetime: to_datetime,
    Host: to_host,
    typing.List[str]: to_list,
    LoadBalancerErrorReason: to_loadbalancer_error_reason,
    UserAgent: to_user_agent,
    HttpRequest: to_http_request,
}


def to_python(value, field):
    if value == '-':
        return None

    parse_func = TYPE_MAPPINGS.get(field.type)
    if parse_func:
        return parse_func(value)

    try:
        return field.type(value)
    except TypeError:
        raise ValueError(f'Got {type(value)} for {field.name} expected {field.type}')


def log_parser(content, log_type):
    fields = dataclasses.fields(log_type.model)
    for row in csv.reader(content, delimiter=log_type.delimiter):
        if not row or row[0].startswith('#'):
            continue
        yield log_type.model(*[
            to_python(value, field)
            for value, field in zip(row, fields)
        ])
