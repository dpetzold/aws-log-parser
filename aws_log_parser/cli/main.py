import argparse
import logging

from collections import Counter
from dataclasses import dataclass
from urllib.parse import urlparse

from ..parser import AwsLogParser
from ..models import LogType

from .aws import AwsClient

logger = logging.getLogger(__name__)


@dataclass
class AwsLogParserCli:

    region: str
    profile: str

    @property
    def aws_client(self):
        return AwsClient(region=self.region, profile=self.profile)

    def aws_service(self, service_name):
        return self.aws_client.service_factory(service_name)

    @property
    def ec2_service(self):
        return self.aws_service("ec2")

    @property
    def s3_service(self):
        return self.aws_service("s3")

    def read_file(self, path):
        with open(path) as log_data:
            yield from AwsLogParser(
                log_type=LogType.ClassicLoadBalancer,
            ).parse(log_data.readlines())

    def read_files(self, paths):
        for path in paths:
            yield from self.read_file(path)

    def count_hosts(self, entries):
        hosts = Counter()
        for entry in entries:
            hosts[entry.client.ip] += 1

        names = self.ec2_service.resolve_ip_addresses(list(hosts.keys()))

        for host, count in hosts.items():
            print(f"{names[host]} {count:,}")

    def run(self, args):
        parsed = urlparse(args.url)

        if parsed.scheme == "file":
            entries = self.read_files(parsed.path)

        elif parsed.scheme == "s3":
            entries = self.s3_service.read_keys(
                parsed.netloc, parsed.path.lstrip("/"), endswith=".log"
            )

        else:
            raise ValueError(f"Unknown scheme {parsed.scheme}")

        self.count_hosts(entries)


def main():
    parser = argparse.ArgumentParser(description="Parse AWS log data.")
    parser.add_argument(
        "url",
        help="Url to the file to parse",
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
