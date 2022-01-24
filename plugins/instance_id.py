from dataclasses import dataclass

from aws_log_parser.aws.plugin import AwsPluginBase


@dataclass
class AwsPluginInstanceId(AwsPluginBase):
    """
    Resolve the instance_id from its private ip address.
    """

    attr_name: str = "instance_id"

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

    def augment(self, log_entries):

        instance_ids = self.lookup({log_entry.client_ip for log_entry in log_entries})

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, instance_ids.get(log_entry.client_ip))
            yield log_entry
