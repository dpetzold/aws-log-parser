import concurrent.futures
import csv
import gzip
import importlib
import importlib.util
import logging
import sys
import typing

from dataclasses import dataclass, fields, field
from pathlib import Path
from urllib.parse import urlparse

from .aws import AwsClient
from .models import (
    LogFormat,
)
from .util import batcher

from .parser import to_python


logger = logging.getLogger(__name__)


@dataclass
class AwsLogParser:

    log_type: LogFormat

    # Optional
    region: typing.Optional[str] = None
    profile: typing.Optional[str] = None
    file_suffix: str = ".log"
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

    def _parse(self, content: typing.List[str]):
        model_fields = fields(self.log_type.model)
        for row in csv.reader(content, delimiter=self.log_type.delimiter):
            if not row[0].startswith("#"):
                yield self.log_type.model(  # type: ignore
                    *[
                        to_python(value, field)
                        for value, field in zip(row, model_fields)
                    ]
                )

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

        kwargs = {}
        if hasattr(plugin, "aws_client") and plugin.aws_client is None:
            kwargs = {"aws_cliend": self.aws_client}
        return getattr(module, plugin_classs)(**kwargs)

    def run_plugins(self, log_entries):
        for plugin in self.plugins_loaded:
            log_entries = plugin.init(log_entries)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.plugins_loaded),
        ) as executor:

            futures = [
                executor.submit(plugin.populate_table) for plugin in self.plugins_loaded
            ]

            concurrent.futures.wait(futures)

            for plugin in self.plugins_loaded:
                print(f"Augmenting {plugin.produced_attr}")
                log_entries = plugin.augment(log_entries)

            yield from log_entries

    def parse(self, content):
        log_entries = self._parse(content)

        yield from self.run_plugins(log_entries)

        for plugin in self.plugins_loaded:
            if hasattr(plugin, "requests"):
                print(f"{plugin.requests:,} requests")

    def yield_file(self, path):
        with open(path) as log_data:
            yield from log_data.readlines()

    def yield_gzip(self, path):
        with gzip.open(path, "rt") as f:
            yield from f.readlines()

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

        yield_func = self.yield_gzip if path.suffix == ".gz" else self.yield_file

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
