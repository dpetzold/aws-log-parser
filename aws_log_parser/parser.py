import csv
import dataclasses


def to_python(value, field):
    if value == '-':
        return None
    return field.type(value)


def log_parser(content, log_type):
    fields = dataclasses.fields(log_type.model)
    for row in csv.reader(content, delimiter=log_type.delimiter):
        if not row[0].startswith('#'):
            yield log_type.model(*[
                to_python(value, field) for value, field in zip(row, fields)
            ])
