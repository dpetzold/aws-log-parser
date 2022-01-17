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
    max_workers: int = 10

    _results: typing.Dict[str, typing.Optional[str]] = field(default_factory=dict)

    def async_query(self, values):

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            query_future = {
                executor.submit(self.query, value): value for value in values
            }

            for future in concurrent.futures.as_completed(query_future):
                value = query_future[future]
                try:
                    result = future.result()
                except Exception:
                    logger.error(f"{value} generated an exception", exc_info=True)
                else:
                    if value:
                        self._results[value] = result

    def lookup(self, values):

        unknown = values - self._results.keys()

        print(
            " ".join(
                [
                    f"unknown={len(unknown):,}",
                    f"found={len(values)-len(unknown)}",
                    f"total={len(values):,}",
                ]
            )
        )

        start = time_ms()
        if unknown:
            self.async_query(list(unknown))
        spent = time_ms() - start
        print(f"{spent/1000.0:.2f}s avg={spent/len(unknown):.2f}ms")

        return self._results

    def query(self, _):
        raise NotImplementedError

    def augment(self, _):
        raise NotImplementedError
