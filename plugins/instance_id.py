from dataclasses import dataclass
from functools import lru_cache

from aws_log_parser.aws import AwsClient


@dataclass
class AwsPluginInstanceId:
    """
    Resolve the instance_id from its private ip address.
    """

    aws_client: AwsClient
    attr_name: str = "instance_id"
    batch_size: int = 256

    def __hash__(self):
        return hash(repr(self))

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def instance_id(self, ni):

        if ni["InterfaceType"] == "branch":
            ecs_service = self.aws_client.get_tag(ni["TagSet"], "aws:ecs:serviceName")
            return f"ecs:{ecs_service}"

        return ni["Attachment"]["InstanceId"] if ni.get("Attachment") else None

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

        return {ni["PrivateIpAddress"]: self.instance_id(ni) for ni in nis}

    def augment(self, log_entry):
        instance_ids = self.instance_ids(log_entry.client_ip)
        setattr(log_entry, self.attr_name, instance_ids.get(log_entry.client_ip))
        return log_entry
