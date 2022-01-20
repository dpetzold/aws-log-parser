import concurrent.futures
import logging
import pprint
import typing

from dataclasses import dataclass, field

from .util import batcher

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserPlugin:
    """
    Resolve the instance_id from its private ip address.
    """

    batch_size: int = 1
    max_workers: typing.Optional[int] = None

    # Overriden
    produced_attr: typing.Optional[str] = None
    consumed_attr: typing.Optional[str] = None

    # Internal
    _results: typing.Dict[str, typing.Optional[str]] = field(default_factory=dict)

    def run(self, values):
        logger.debug(pprint.pformat(values))

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:

            futures = {
                executor.submit(self.query, batch)
                for batch in batcher(values, self.batch_size)
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self._results.update(result)

    def query(self, _):
        raise NotImplementedError

    def augment(self, log_entry):
        if self.consumed_attr and self.produced_attr:
            value = self._results.get(getattr(log_entry, self.consumed_attr))
            logger.debug(f"{self.produced_attr}: {self.consumed_attr}={value}")
            setattr(log_entry, self.produced_attr, value)
