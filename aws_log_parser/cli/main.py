import argparse
import logging

from collections import Counter
from dataclasses import dataclass

from ..aws import AwsClient
from ..interface import AwsLogParser
from ..models import LogType

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserCli:

    region: str
    profile: str

    @property
    def aws_client(self):
        return AwsClient(region=self.region, profile=self.profile)

    @property
    def ec2_service(self):
        return self.aws_client.service_factory("ec2")

    def count_hosts(self, entries):
        hosts = Counter()
        for entry in entries:
            hosts[entry.client.ip] += 1

        names = self.ec2_service.resolve_ip_addresses(list(hosts.keys()))

        for host, count in hosts.items():
            print(f"{names[host]} {count:,}")

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

    args = parser.parse_args()

    AwsLogParserCli(
        region=args.region,
        profile=args.profile,
    ).run(args)
