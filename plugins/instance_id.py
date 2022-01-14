from dataclasses import dataclass
from functools import lru_cache

from aws_log_parser.aws import AwsClient


@dataclass
class AwsLogParserPluginInstanceId:

    aws_client: AwsClient
    attr_name: str = "instance_id"

    def __hash__(self):
        return hash(repr(self))

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    @lru_cache
    def instance_ids(self, *ips):
        nis = self.ec2_client.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ips,
                },
            ],
        )["NetworkInterfaces"]

        return {ni["PrivateIpAddress"]: ni["Attachment"]["InstanceId"] for ni in nis}

    def augment(self, log_entry):
        instance_ids = self.instance_ids(log_entry.client_ip)
        setattr(log_entry, self.attr_name, instance_ids.get(log_entry.client_ip))
        return log_entry
