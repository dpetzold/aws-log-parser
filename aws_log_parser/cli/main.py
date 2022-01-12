import argparse
import logging

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from ..aws import AwsClient
from ..interface import AwsLogParser
from ..models import LogType

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserCli:

    region: str
    profile: str

    def __hash__(self):
        return hash(repr(self))

    @property
    def aws_client(self):
        return AwsClient(region=self.region, profile=self.profile)

    @property
    def ec2_service(self):
        return self.aws_client.aws_client("ec2")

    def get_tag(self, tags, name):
        for tag in tags:
            if tag["Key"] == name:
                return tag["Value"]

    @lru_cache
    def instance_name(self, instance_id):
        reservations = self.ec2_service.describe_instances(
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

            name = self.get_tag(instance["Tags"], "Name")

            d.update({private_ip: name for private_ip in private_ips})

        return d

    @lru_cache
    def resolve_ip_addresses(self, *ips):
        nis = self.ec2_service.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ips,
                },
            ],
        )["NetworkInterfaces"]

        d = {}
        for ni in nis:
            d.update(self.instance_name(ni["Attachment"]["InstanceId"]))
        return d

    def count_hosts(self, entries):
        hosts = Counter()
        for entry in entries:
            hosts[entry.client.ip] += 1

        names = self.resolve_ip_addresses(*list(hosts.keys()))

        for host, count in sorted(hosts.items(), key=lambda t: t[1]):
            print(f"{names.get(host, host)}: {count:,}")

    def run(self, args):
        self.count_hosts(AwsLogParser(log_type=args.log_type).read_url(args.url))


def main():

    parser = argparse.ArgumentParser(description="Parse AWS log data.")
    parser.add_argument(
        "url",
        help="Url to the file to parse",
    )

    parser.add_argument(
        "--log-type",
        type=lambda x: getattr(LogType, x),
        help="The the log type.",
    )

    parser.add_argument(
        "--profile",
        help="The aws profile to use.",
    )

    parser.add_argument(
        "--region",
        help="The aws region to use.",
    )
    parser.add_argument(
        "--count-hosts",
        help="Count the number of hosts",
    )
    parser.add_argument(
        "--instance-id",
    )

    args = parser.parse_args()

    cli = AwsLogParserCli(
        region=args.region,
        profile=args.profile,
    )

    if args.instance_id:
        return cli.instance_name(args.instance_id)

    cli.run(args)
