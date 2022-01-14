from dataclasses import dataclass
from functools import lru_cache

from aws_log_parser.aws import AwsClient


@dataclass
class AwsLogParserPluginInstanceName:

    aws_client: AwsClient
    attr_name: str = "instance_id"

    def __hash__(self):
        return hash(repr(self))

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    @lru_cache
    def instance_name(self, instance_id):
        reservations = self.ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "instance-id",
                    "Values": [instance_id],
                },
            ]
        )["Reservations"]

        instances = [
            instance
            for reservation in reservations
            for instance in reservation["Instances"]
        ]

        d = {}
        for instance in instances:
            private_ips = [
                address["PrivateIpAddress"]
                for ni in instance["NetworkInterfaces"]
                for address in ni["PrivateIpAddresses"]
            ]

            name = self.aws_client.get_tag(instance["Tags"], "Name")

            d.update({private_ip: name for private_ip in private_ips})

        return d

    def augment(self, log_entry):
        setattr(
            log_entry,
            self.attr_name,
            self.instance_name(log_entry.client_ip).get(log_entry.client_ip),
        )
