from dataclasses import dataclass

from .client import AwsClient
from ..plugin import AwsLogParserPlugin


@dataclass(kw_only=True)
class AwsPluginBase(AwsLogParserPlugin):
    aws_client: AwsClient

    @property
    def ec2_client(self):
        if self.aws_client:
            return self.aws_client.ec2_client
