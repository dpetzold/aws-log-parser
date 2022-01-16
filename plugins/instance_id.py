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
    batch_size: int = 1024 * 5

    _instance_mappings: typing.Dict[str, str] = field(default_factory=dict)

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def instance_id(self, ni):

        if ni["InterfaceType"] == "branch":
            ecs_service = self.aws_client.get_tag(ni["TagSet"], "aws:ecs:serviceName")
            return f"ecs:{ecs_service}"

        return ni["Attachment"]["InstanceId"] if ni.get("Attachment") else None

    def query(self, *ips):
        pprint(ips)
        nis = self.ec2_client.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ips,
                },
            ],
        )["NetworkInterfaces"]

        return {ni["PrivateIpAddress"]: self.instance_id(ni) for ni in nis}

    def instance_ids(self, *ips):

        unknown = []

        for ip in ips:
            instance_id = self._instance_mappings.get(ip)
            if not instance_id:
                unknown.append(ip)

        if unknown:
            self._instance_mappings.update(self.query(*unknown))

        return self._instance_mappings

    def augment(self, batch):

        instance_ids = self.instance_ids(*{log_entry.client_ip for log_entry in batch})

        for log_entry in batch:
            setattr(log_entry, self.attr_name, instance_ids.get(log_entry.client_ip))
            yield log_entry
