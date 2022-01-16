import typing
from dataclasses import dataclass, field

from pprint import pprint

from aws_log_parser.aws import AwsClient


@dataclass
class AwsPluginBase:
    """
    Resolve the instance_id from its private ip address.
    """

    aws_client: AwsClient
    batch_size: int = 1024 * 8

    _cache: typing.Dict[str, str] = field(default_factory=dict)

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def lookup(self, ips):

        unknown = []

        # xxx: set atrimatic
        for ip in ips:
            instance_id = self._cache.get(ip)
            if not instance_id:
                unknown.append(ip)

        if unknown:
            self.query(unknown)

        return self._cache

    def query(self, _):
        raise NotImplementedError

    def augment(self, _):
        raise NotImplementedError
