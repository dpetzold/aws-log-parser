import typing
from dataclasses import dataclass, field

from pprint import pprint

from aws_log_parser.aws import AwsClient


@dataclass
class AwsPluginInstanceName:

    aws_client: AwsClient
    attr_name: str = "instance_name"
    batch_size: int = 1024 * 8

    _cache: typing.Dict[str, str] = field(default_factory=dict)

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def query(self, instance_ids):
        pprint(instance_ids)
        reservations = self.ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "instance-id",
                    "Values": instance_ids,
                },
            ]
        )["Reservations"]

        instances = [
            instance
            for reservation in reservations
            for instance in reservation["Instances"]
        ]

        for instance in instances:
            private_ips = [
                address["PrivateIpAddress"]
                for ni in instance["NetworkInterfaces"]
                for address in ni["PrivateIpAddresses"]
            ]

            name = self.aws_client.get_tag(instance["Tags"], "Name")

            self._cache.update({private_ip: name for private_ip in private_ips})

        return self._cache

    def instance_names(self, instance_ids):

        unknown = []

        for instance_id in instance_ids:
            instance_name = self._cache.get(instance_id)
            if not instance_name:
                unknown.append(instance_id)

        if unknown:
            self.query(unknown)

        return self._cache

    def augment(self, log_entries):

        instance_names = self.instance_names(
            {
                log_entry.instance_id
                for log_entry in log_entries
                if (
                    log_entry.instance_id
                    and not log_entry.instance_id.startswith("ecs:")
                )
            }
        )

        pprint(instance_names)

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, instance_names.get(log_entry.client_ip))
            yield log_entry
