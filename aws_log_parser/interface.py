import csv
import typing
import importlib
import importlib.util
import re
import sys

from dataclasses import dataclass, fields, field
from pathlib import Path
from urllib.parse import urlparse

from .aws import AwsClient
from .io import FileIterator
from .models import (
    LogFormat,
    LogFormatType,
)
from .util import batcher

from .parser import to_python


@dataclass
class AwsLogParser:
    log_type: LogFormat

    # Optional
    region: typing.Optional[str] = None
    profile: typing.Optional[str] = None
    file_suffix: str = ".log"
    regex_filter: typing.Optional[str] = None
    verbose: bool = False

    plugin_paths: typing.List[typing.Union[str, Path]] = field(default_factory=list)
    plugins: typing.List[str] = field(default_factory=list)

    def __post_init__(self):
        self.aws_client = AwsClient(
            region=self.region, profile=self.profile, verbose=self.verbose
        )

        self.plugins_loaded = [
            self.load_plugin(
                plugin,
                self.plugin_paths[0],
            )
            for plugin in self.plugins
        ]

    def load_plugin(self, plugin, plugin_path):
        plugin_module, plugin_classs = plugin.split(":")
        spec = importlib.util.spec_from_file_location(
            plugin_module, f"{plugin_path}/{plugin_module}.py"
        )
        if spec is None:
            raise ValueError("{plugin} not found")

        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_module] = module
        spec.loader.exec_module(module)  # type: ignore
        return getattr(module, plugin_classs)(aws_client=self.aws_client)

    def run_plugin(self, plugin, log_entries):
        for batch in batcher(log_entries, plugin.batch_size):
            yield from plugin.augment(batch)

    def parse_csv(self, content):
        model_fields = fields(self.log_type.model)
        assert self.log_type.delimiter
        for row in csv.reader(content, delimiter=self.log_type.delimiter):
            if not row[0].startswith("#"):
                yield self.log_type.model(
                    *[
                        to_python(value, field)
                        for value, field in zip(row, model_fields)
                    ]
                )

    def parse_json(self, records):
        for record in records:
            yield self.log_type.model.from_json(record)  # type: ignore

    def parse(self, content):
        parse_func = (
            self.parse_json
            if self.log_type.type == LogFormatType.JSON
            else self.parse_csv
        )
        log_entries = parse_func(content)
        for plugin in self.plugins_loaded:
            log_entries = self.run_plugin(plugin, log_entries)
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
        if not isinstance(path, Path):
            path = Path(path)
        if self.verbose:
            print(f"Reading file://{path}")
        yield from self.parse(FileIterator(path, gzipped=path.suffix == ".gz"))

    def read_files(self, pathname):
        """
        Yield parsed log entries from the files in the given path.
        Low level function used by ``parse_url``.

        :param pathname: The path to the files.
        :type kind: str
        :return: Parsed log entries.
        :rtype: Dependant on log_type.
        """
        base_path = Path(pathname)
        if base_path.is_dir():
            if self.regex_filter:
                reo = re.compile(self.regex_filter)
                for path in base_path.iterdir():
                    if reo.match(path.name) and path.is_file():
                        yield from self.read_file(path)
            else:
                for path in base_path.glob(f"**/*{self.file_suffix}"):
                    yield from self.read_file(path)
        else:
            yield from self.read_file(base_path)

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
            self.aws_client.s3_service.read_keys(
                bucket,
                prefix,
                endswith=endswith if endswith else self.file_suffix,
                regex_filter=self.regex_filter,
            )
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
            )
        else:
            raise ValueError(f"Unknown scheme {parsed.scheme}")
