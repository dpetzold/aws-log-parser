import csv
import typing

from dataclasses import dataclass, fields
from pathlib import Path
from urllib.parse import urlparse

from .aws import AwsClient
from .models import (
    LogFormat,
)

from .parser import to_python


@dataclass
class AwsLogParser:

    log_type: LogFormat
    file_suffix: str = ".log"

    # Optional
    region: typing.Optional[str] = None
    profile: typing.Optional[str] = None

    def __post_init__(self):
        self.aws_client = AwsClient(region=self.region, profile=self.profile)

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
        """
        Yield parsed log entries from the given file.
        Low level function used by ``parse_files``.

        :param path: The path to the file.
        :type kind: str
        :return: Parsed log entries.
        :rtype: Dependant on log_type.
        """
        with open(path) as log_data:
            yield from self.parse(log_data.readlines())

    def read_files(self, pathname):
        """
        Yield parsed log entries from the files in the given path.
        Low level function used by ``parse_url``.

        :param pathname: The path to the files.
        :type kind: str
        :return: Parsed log entries.
        :rtype: Dependant on log_type.
        """
        path = Path(pathname)
        if path.is_file():
            yield from self.read_file(path)
        else:
            for p in path.glob(f"**/*{self.file_suffix}"):
                yield from self.read_file(p)

    def read_s3(self, bucket, prefix, endswith=None):
        """
        Yield parsed log entries from the given s3 url.
        Low level function used by ``parse_url``.

        :param bucket: The S3 bucket.
        :type kind: str
        :param prefix: The S3 prefix.
        :type kind: str
        :return: Parsed log entries.
        :rtype: Dependant on log_type.
        """
        yield from self.parse(
            self.aws_client.s3_service.read_keys(bucket, prefix, endswith=endswith)
        )

    def read_url(self, url):
        """
        Yield parsed log entries from the given url. The file:// and s3://
        schemes are currently supported.

        :param url: The url to read from. Partial path's are supported
            for s3 urls. For example::

                s3://bucket/prefix/

            or you can pass the full path to the file::

                s3://bucket/prefix/logfile.log

        :type kind: str
        :raise ValueError: If the url schema is not known.
        :return: Parsed log entries.
        :rtype: Dependant on log_type.

        """
        parsed = urlparse(url)

        if parsed.scheme == "file":
            yield from self.read_files(parsed.path)

        elif parsed.scheme == "s3":
            yield from self.read_s3(
                parsed.netloc,
                parsed.path.lstrip("/"),
                endswith=self.file_suffix,
            )

        else:
            raise ValueError(f"Unknown scheme {parsed.scheme}")
