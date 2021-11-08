from dataclasses import dataclass
from functools import cache

from .aws import AwsService


@dataclass
class Ec2Service(AwsService):
    def __hash__(self):
        return hash(self.__module__)

    @property
    def client(self):
        return self.aws_client.aws_client("ec2")

    @cache
    def get_instances(self, *ip_addresses):
        instance_ids = [
            interface["Attachment"]["InstanceId"]
            for interface in self.client.describe_network_interfaces(
                Filters=[
                    {
                        "Name": "addresses.private-ip-address",
                        "Values": ip_addresses,
                    },
                ],
            )["NetworkInterfaces"]
            if interface.get("Attachment")
        ]

        instances = []

        for reservation in self.client.describe_instances(InstanceIds=instance_ids)[
            "Reservations"
        ]:
            instances.extend(reservation["Instances"])

        return instances

    def resolve_ip_addresses(self, ip_addresses):

        names = {}

        instances = self.get_instances(*ip_addresses)

        for instance in instances:
            name = self.get_tag(instance["Tags"], "Name")
            for interface in instance["NetworkInterfaces"]:
                names[interface["PrivateIpAddress"]] = name

        return names
