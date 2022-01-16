import typing

from dataclasses import dataclass

from .client import AwsClient
from ..plugin import AwsLogParserPlugin


@dataclass
class AwsPluginBase(AwsLogParserPlugin):
    aws_client: typing.Optional[AwsClient] = None

    @property
    def ec2_client(self):
        if self.aws_client:
            return self.aws_client.ec2_client
