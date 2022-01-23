import concurrent.futures
import dataclasses
import importlib
import importlib.util
import logging
import sys
import typing

from collections import defaultdict
from dataclasses import dataclass, field, make_dataclass
from pathlib import Path

from pprint import pprint  # noqa

from ..aws import AwsClient
from ..util import batcher

logger = logging.getLogger(__name__)


@dataclass
class PluginRunner:

    aws_client: AwsClient

    plugin_paths: typing.List[typing.Union[str, Path]] = field(default_factory=list)
    plugins: typing.List[str] = field(default_factory=list)

    consumed_attrs: typing.Set[str] = field(default_factory=set)
    produced_attrs: typing.Set[str] = field(default_factory=set)

    def __post_init__(self):

        self.plugins_loaded = [
            self.load_plugin(
                plugin,
                self.plugin_paths[0],
            )
            for plugin in self.plugins
        ]

        self.consumed_attrs = {plugin.consumed_attr for plugin in self.plugins_loaded}
        self.produced_attrs = {plugin.produced_attr for plugin in self.plugins_loaded}

    def make_model(self, model):
        # Create a new LogEntry model with the plugin fields.
        new_fields = []
        for plugin in self.plugins_loaded:
            for _field in dataclasses.fields(plugin):
                if _field.name == "produced_attr":
                    new_fields.append(
                        (
                            _field.default,
                            _field.metadata["type"] if _field.metadata else _field.type,
                            field(default=None, init=False),
                        )
                    )

        return (
            make_dataclass("LogEntry", fields=new_fields, bases=(model,))
            if new_fields
            else model
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

    def get_consumed_attr_values(self, log_entries):

        consumed_attr_values = defaultdict(set)
        for log_entry in log_entries:
            for consumed_attr in self.consumed_attrs:
                if consumed_attr not in self.produced_attrs:
                    consumed_attr_values[consumed_attr].add(
                        getattr(log_entry, consumed_attr)
                    )

        return consumed_attr_values

    def run(self, log_entries):
        """
        Run the plugins concurrently.
        """
        log_entries = list(log_entries)

        consumed_attr_values = self.get_consumed_attr_values(log_entries)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.plugins_loaded),
        ) as executor:

            futures = {
                executor.submit(
                    plugin.run, consumed_attr_values[plugin.consumed_attr]  # type: ignore
                )
                for plugin in self.plugins_loaded
                if plugin.consumed_attr not in self.produced_attrs
            }

            concurrent.futures.wait(futures)
            # Check for exceptions
            for future in futures:
                try:
                    future.result()
                except Exception as exc:
                    logger.warn(str(exc), exc_info=True)

        for log_entry in log_entries:
            for plugin in self.plugins_loaded:
                if plugin.consumed_attr not in self.produced_attrs:
                    plugin.augment(log_entry)

        # Run plugins with dependant fields.
        for plugin in self.plugins_loaded:
            if plugin.consumed_attr in self.produced_attrs:
                attrs = {
                    getattr(log_entry, plugin.consumed_attr)
                    for log_entry in log_entries
                    if getattr(log_entry, plugin.consumed_attr)
                }
                for batch in batcher(attrs, plugin.batch_size):
                    plugin.run(batch)

        for log_entry in log_entries:
            for plugin in self.plugins_loaded:
                if plugin.consumed_attr in self.produced_attrs:
                    plugin.augment(log_entry)

        for plugin in self.plugins_loaded:
            if hasattr(plugin, "requests"):
                print(f"{plugin.produced_attr}: {plugin.requests:,} requests")

        yield from log_entries
