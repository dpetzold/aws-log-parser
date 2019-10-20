import csv
import dataclasses
import datetime
import typing

from .models import (
    Host,
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


def to_python(value, field):
    if value == '-':
        return None

    if field.type == datetime.date:
        return to_date(value)

    if field.type == datetime.time:
        return to_time(value)

    if field.type == datetime.datetime:
        return to_datetime(value)

    if field.type == Host:
        return to_host(value)

    if field.type == typing.List[str]:
        return to_list(value)

    if field.type == LoadBalancerErrorReason:
        return to_loadbalancer_error_reason(value)

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
