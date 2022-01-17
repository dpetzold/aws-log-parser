import concurrent.futures
import logging
import typing

from dataclasses import dataclass, field

from .util import time_ms

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserPlugin:
    """
    Resolve the instance_id from its private ip address.
    """

    batch_size: int = 1024 * 8
    max_workers: typing.Optional[int] = None

    _items: typing.Set[str] = field(default_factory=set)
    _results: typing.Dict[str, typing.Optional[str]] = field(default_factory=dict)

    def async_query(self, values):

        with concurrent.futures.ThreadPoolExecutor(
            # max_workers=self.max_workers
        ) as executor:
            futures = {executor.submit(self.query, value): value for value in values}

            for future in concurrent.futures.as_completed(futures):
                value = futures[future]
                try:
                    result = future.result()
                except Exception:
                    logger.error(f"{value} generated an exception", exc_info=True)
                else:
                    if value:
                        self._results[value] = result

    def init(self, log_entries):
        print(f"{self.produced_attr}: init ({len(self._items)})")
        _log_entries = []
        for log_entry in log_entries:
            self._items.add(getattr(log_entry, self.consumed_attr))
            _log_entries.append(log_entry)
        print(f"{self.produced_attr}: init completed ({len(self._items)})")
        return _log_entries

    def populate_table(self):
        print(f"{self.produced_attr}: populating ({len(self._items)})")

        start = time_ms()
        self.async_query(self._items)
        spent = time_ms() - start
        print(
            f"{self.produced_attr}: {spent/1000.0:.2f}s avg={spent/len(self._items):.2f}ms"
        )

    def query(self, _):
        raise NotImplementedError

    def augment(self, _):
        raise NotImplementedError
