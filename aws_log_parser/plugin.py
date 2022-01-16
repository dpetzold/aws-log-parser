import typing
from dataclasses import dataclass, field


@dataclass
class AwsLogParserPlugin:
    """
    Resolve the instance_id from its private ip address.
    """

    batch_size: int = 1024 * 8

    _cache: typing.Dict[str, str] = field(default_factory=dict)

    def lookup(self, ips):

        unknown = ips - self._cache.keys()

        if unknown:
            self.query(list(unknown))

        return self._cache

    def query(self, _):
        raise NotImplementedError

    def augment(self, _):
        raise NotImplementedError
