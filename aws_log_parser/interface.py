import csv
import logging
import typing

from dataclasses import dataclass, fields, field
from pathlib import Path
from urllib.parse import urlparse

from pprint import pprint  # noqa

from .aws import AwsClient
from .models import (
    LogFormat,
)

from .parser import to_python
from .plugin import PluginRunner
from .util import yield_gzip, yield_file


logger = logging.getLogger(__name__)


@dataclass
class AwsLogParser:

    log_type: LogFormat

    # Optional
    aws_client: typing.Optional[AwsClient] = None
    aws_region: typing.Optional[str] = None
    aws_profile: typing.Optional[str] = None
    file_suffix: str = ".log"
    verbose: bool = False

    # Plugin
    plugin_paths: typing.List[typing.Union[str, Path]] = field(default_factory=list)
    plugins: typing.List[str] = field(default_factory=list)
    plugin_runner: typing.Optional[PluginRunner] = None

    model: typing.Optional[typing.Type] = None

    def __post_init__(self):
        self.aws_client = AwsClient(
            region=self.aws_region, profile=self.aws_profile, verbose=self.verbose
        )

        self.plugin_runner = PluginRunner(
            aws_client=self.aws_client,
            plugin_paths=self.plugin_paths,
            plugins=self.plugins,
        )

        self.model = self.plugin_runner.make_model(self.log_type.model)

    def _parse(self, content):
        model_fields = fields(self.log_type.model)
        for row in csv.reader(content, delimiter=self.log_type.delimiter):
            if not row[0].startswith("#"):
                yield self.model(  # type: ignore
                    *[
                        to_python(value, field)
                        for value, field in zip(row, model_fields)
                    ]
                )

    def parse(self, content):
        log_entries = self._parse(content)
        if self.plugin_runner:
            yield from self.plugin_runner.run(log_entries)
        yield from log_entries

    def read_file(self, path):
        """
        Yield parsed log entries from the given file.
        Low level function used by ``parse_files``.

        :param path: The path to the file.
        :type kind: str
        :return: Parsed log entries.
        :rtype: Dependant on log_type.
        """
        if self.verbose:
            print(f"Reading file://{path}")

        yield_func = yield_gzip if path.suffix == ".gz" else yield_file

        yield from self.parse(yield_func(path))

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
                yield self.read_file(p)

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
        assert self.aws_client

        for keys in self.aws_client.s3_service.read_keys(
            bucket, prefix, endswith=endswith
        ):
            yield self.parse(keys)

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
            log_entries = self.read_files(parsed.path)

        elif parsed.scheme == "s3":
            log_entries = self.read_s3(
                parsed.netloc,
                parsed.path.lstrip("/"),
                endswith=self.file_suffix,
            )

        else:
            raise ValueError(f"Unknown scheme {parsed.scheme}")

        yield from log_entries
