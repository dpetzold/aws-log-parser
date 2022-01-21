import logging
import pprint
from dataclasses import dataclass

from aws_log_parser.aws.plugin import AwsPluginBase

logger = logging.getLogger(__name__)


@dataclass
class AwsPluginInstanceId(AwsPluginBase):
    """
    Resolve the instance_id from its private ip address.
    """

    consumed_attr: str = "client_ip"
    produced_attr: str = "instance_id"
    batch_size: int = 128

    def instance_id(self, ni):
        assert self.aws_client
        if ni["InterfaceType"] == "branch":
            ecs_service = self.aws_client.get_tag(ni["TagSet"], "aws:ecs:serviceName")
            return f"ecs:{ecs_service}"

        return ni["Attachment"].get("InstanceId") if ni.get("Attachment") else None

    def query(self, ips):
        assert self.aws_client
        logger.info(len(ips))
        nis = self.aws_client.ec2_client.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ips,
                },
            ],
        )["NetworkInterfaces"]

        logger.debug(len(nis))
        logger.debug(pprint.pformat(nis[0]))
        logger.debug(pprint.pformat(self.instance_id(nis[0])))

        d = {ni["PrivateIpAddress"]: self.instance_id(ni) for ni in nis}
        logger.debug(len(d))
        return d
