import csv
import typing

from dataclasses import dataclass, fields
from urllib.parse import urlparse

from .aws import AwsClient
from .models import (
    LogFormat,
)

from .parser import to_python


@dataclass
class AwsLogParser:

    log_type: LogFormat

    # Optional
    region: typing.Optional[str] = None
    profile: typing.Optional[str] = None

    @property
    def aws_client(self):
        return AwsClient(region=self.region, profile=self.profile)

    def aws_service(self, service_name):
        return self.aws_client.service_factory(service_name)

    @property
    def s3_service(self):
        return self.aws_service("s3")

    def parse(self, content: typing.List[str]):
        model_fields = fields(self.log_type.model)
        for row in csv.reader(content, delimiter=self.log_type.delimiter):
            if not row[0].startswith("#"):
                yield self.log_type.model(  # type: ignore
                    *[
                        to_python(value, field)
                        for value, field in zip(row, model_fields)
                    ]
                )

    def read_file(self, path):
        with open(path) as log_data:
            yield from self.parse(log_data.readlines())

    def read_files(self, paths):
        for path in paths:
            yield from self.read_file(path)

    def read_s3(self, bucket, prefix, endswith=None):
        yield from self.parse(
            self.s3_service.read_keys(bucket, prefix, endswith=endswith)
        )

    def read_url(self, url):
        parsed = urlparse(url)

        if parsed.scheme == "file":
            yield from self.read_files(parsed.path)

        elif parsed.scheme == "s3":
            yield from self.read_s3(
                parsed.netloc, parsed.path.lstrip("/"), endswith=".log"
            )

        else:
            raise ValueError(f"Unknown scheme {parsed.scheme}")
