import concurrent.futures
import logging
import typing

from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserPlugin:
    """
    Resolve the instance_id from its private ip address.
    """

    batch_size: int = 1024 * 8
    max_workers: typing.Optional[int] = None

    produced_attr: typing.Optional[str] = None
    consumed_attr: typing.Optional[str] = None

    _items: typing.Set[str] = field(default_factory=set)
    _results: typing.Dict[str, typing.Optional[str]] = field(default_factory=dict)

    def run(self, values):

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

    def query(self, _):
        raise NotImplementedError

    def augment(self, log_entry):
        if self.consumed_attr and self.produced_attr:
            setattr(
                log_entry,
                self.produced_attr,
                self._results.get(getattr(log_entry, self.consumed_attr)),
            )
