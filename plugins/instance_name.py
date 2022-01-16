from dataclasses import dataclass

from aws_log_parser.aws.plugin import AwsPluginBase


@dataclass
class AwsPluginInstanceName(AwsPluginBase):

    attr_name: str = "instance_name"

    @property
    def ec2_client(self):
        return self.aws_client.ec2_client

    def query(self, instance_ids):
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

    def augment(self, log_entries):

        instance_names = self.lookup(
            {
                log_entry.instance_id
                for log_entry in log_entries
                if (
                    log_entry.instance_id
                    and not log_entry.instance_id.startswith("ecs:")  # noqa: W503
                )
            }
        )

        for log_entry in log_entries:
            setattr(log_entry, self.attr_name, instance_names.get(log_entry.client_ip))
            yield log_entry
