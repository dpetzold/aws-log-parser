import concurrent.futures
import csv
import dataclasses
import gzip
import importlib
import importlib.util
import logging
import sys
import typing

from collections import defaultdict
from dataclasses import dataclass, fields, field, make_dataclass
from pathlib import Path
from urllib.parse import urlparse

from pprint import pprint  # noqa

from .aws import AwsClient
from .util import batcher
from .models import (
    LogFormat,
)

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

    # Plugin
    plugin_paths: typing.List[typing.Union[str, Path]] = field(default_factory=list)
    plugins: typing.List[str] = field(default_factory=list)

    plugin_consumed_attrs: typing.Set[str] = field(default_factory=set)
    plugin_produced_attrs: typing.Set[str] = field(default_factory=set)

    # Internal
    _plugin_attr_values: typing.Dict[str, typing.List[str]] = field(
        default_factory=lambda: defaultdict(list)
    )

    model: typing.Optional[typing.Type] = None

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

        if self.plugins_loaded:
            # Create a new dataclass with the plugin fields.
            new_fields = []
            for plugin in self.plugins_loaded:
                for _field in dataclasses.fields(plugin):
                    if _field.name == "produced_attr":
                        new_fields.append(
                            (
                                _field.default,
                                _field.metadata["type"]
                                if _field.metadata
                                else _field.type,
                                field(init=False),
                            )
                        )
            self.model = make_dataclass(
                "LogEntry", fields=new_fields, bases=(self.log_type.model,)
            )

        else:
            self.model = self.log_type.model

        self.plugin_consumed_attrs = {
            plugin.consumed_attr for plugin in self.plugins_loaded
        }

        self.plugin_produced_attrs = {
            plugin.produced_attr for plugin in self.plugins_loaded
        }

    def _parse(self, content: typing.List[str]):
        model_fields = fields(self.log_type.model)
        for row in csv.reader(content, delimiter=self.log_type.delimiter):
            if not row[0].startswith("#"):
                yield self.model(  # type: ignore
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

        plugin_cls = getattr(module, plugin_classs)

        requires_aws_client = False
        for _field in dataclasses.fields(plugin_cls):
            if _field.name == "aws_client":
                requires_aws_client = True
                break

        kwargs = {"aws_client": self.aws_client} if requires_aws_client else {}
        return plugin_cls(**kwargs)

    def init_plugins(self, log_entries):

        # XXX: is there a way to not copy here

        _log_entries = []
        for log_entry in log_entries:
            for consumed_attr in self.plugin_consumed_attrs:
                if consumed_attr not in self.plugin_produced_attrs:
                    self._plugin_attr_values[consumed_attr].append(
                        getattr(log_entry, consumed_attr)
                    )
            _log_entries.append(log_entry)

        return _log_entries

    def run_plugins(self, log_entries):
        """
        Run the plugins concurrently.
        """

        log_entries = self.init_plugins(log_entries)

        produced_attrs = {plugin.produced_attr for plugin in self.plugins_loaded}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.plugins_loaded),
        ) as executor:

            futures = {
                executor.submit(
                    plugin.run, self._plugin_attr_values[plugin.consumed_attr]  # type: ignore
                )
                for plugin in self.plugins_loaded
                if plugin.consumed_attr not in produced_attrs
            }

            concurrent.futures.wait(futures)

        for log_entry in log_entries:
            for plugin in self.plugins_loaded:
                if plugin.consumed_attr not in produced_attrs:
                    plugin.augment(log_entry)

        # Run plugins with dependant fields.
        for plugin in self.plugins_loaded:
            if plugin.consumed_attr in produced_attrs:
                for batch in batcher(log_entries, plugin.batch_size):
                    plugin.run(
                        getattr(log_entry, plugin.consumed_attr) for log_entry in batch
                    )

        for log_entry in log_entries:
            for plugin in self.plugins_loaded:
                if plugin.consumed_attr in produced_attrs:
                    plugin.augment(log_entry)

        yield from log_entries

    def parse(self, content):
        log_entries = self._parse(content)

        yield from self.run_plugins(log_entries)

        for plugin in self.plugins_loaded:
            if hasattr(plugin, "requests"):
                print(f"{plugin.produced_attr}: {plugin.requests:,} requests")

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
