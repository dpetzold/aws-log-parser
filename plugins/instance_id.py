import typing
from dataclasses import dataclass, field

from pprint import pprint

from aws_log_parser.aws import AwsClient


@dataclass
class AwsPluginInstanceId:
    """
    Resolve the instance_id from its private ip address.
    """

    aws_client: AwsClient
    attr_name: str = "instance_id"
    batch_size: int = 1024 * 8

    _cache: typing.Dict[str, str] = field(default_factory=dict)

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def instance_id(self, ni):

        if ni["InterfaceType"] == "branch":
            ecs_service = self.aws_client.get_tag(ni["TagSet"], "aws:ecs:serviceName")
            return f"ecs:{ecs_service}"

        return ni["Attachment"]["InstanceId"] if ni.get("Attachment") else None

    def query(self, ips):
        nis = self.ec2_client.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ips,
                },
            ],
        )["NetworkInterfaces"]

        self._cache.update({ni["PrivateIpAddress"]: self.instance_id(ni) for ni in nis})

    def instance_ids(self, ips):

        unknown = []

        # xxx: set atrimatic
        for ip in ips:
            instance_id = self._cache.get(ip)
            if not instance_id:
                unknown.append(ip)

        if unknown:
            self.query(unknown)

        return self._cache

    def augment(self, log_entries):

        instance_ids = self.instance_ids(
            {log_entry.client_ip for log_entry in log_entries}
        )

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, instance_ids.get(log_entry.client_ip))
            yield log_entry
