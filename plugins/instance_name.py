import logging
from dataclasses import dataclass

from aws_log_parser.aws.plugin import AwsPluginBase

logger = logging.getLogger(__name__)


@dataclass
class AwsPluginInstanceName(AwsPluginBase):

    consumed_attr: str = "instance_id"
    produced_attr: str = "instance_name"
    batch_size: int = 128

    def query(self, instance_ids):
        assert self.aws_client
        logger.debug(len(instance_ids))

        reservations = self.aws_client.ec2_client.describe_instances(
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

        results = {}
        for instance in instances:

            name = self.aws_client.get_tag(instance["Tags"], "Name")

            private_ips = [
                address["PrivateIpAddress"]
                for ni in instance["NetworkInterfaces"]
                for address in ni["PrivateIpAddresses"]
            ]

            results.update({private_ip: name for private_ip in private_ips})

        return results

    def augment(self, log_entry):
        value = self._results.get(
            log_entry.client_ip,
            log_entry.instance_id if log_entry.instance_id else log_entry.client_ip,
        )

        assert value is not None, str(log_entry)

        setattr(
            log_entry,
            self.produced_attr,
            value,
        )
