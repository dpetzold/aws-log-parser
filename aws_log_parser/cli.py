import argparse
import boto3

import logging

from collections import Counter
from functools import cache
from urllib.parse import urlparse

from .parser import AwsLogParser
from .models import LogType

logger = logging.getLogger(__name__)


ec2_client = boto3.client("ec2")
s3_client = boto3.client("s3")


def parse_file(path):
    with open(path) as log_data:
        yield from AwsLogParser(
            log_type=LogType.ClassicLoadBalancer,
        ).parse(log_data.readlines())


def get_tag(tags, name):
    for tag in tags:
        if tag["Key"] == name:
            return tag["Value"]


@cache
def get_instances(*ip_addresses):
    instance_ids = [
        interface["Attachment"]["InstanceId"]
        for interface in ec2_client.describe_network_interfaces(
            Filters=[
                {
                    "Name": "addresses.private-ip-address",
                    "Values": ip_addresses,
                },
            ],
        )["NetworkInterfaces"]
    ]

    instances = []

    for reservation in ec2_client.describe_instances(InstanceIds=instance_ids)[
        "Reservations"
    ]:
        instances.extend(reservation["Instances"])

    return instances


def resolve_ip_addresses(ip_addresses):

    names = {}

    instances = get_instances(*ip_addresses)

    for instance in instances:
        name = get_tag(instance["Tags"], "Name")
        for interface in instance["NetworkInterfaces"]:
            names[interface["PrivateIpAddress"]] = name

    return names


def count_hosts(entries):
    hosts = Counter()
    for entry in entries:
        hosts[entry.client.ip] += 1

    names = resolve_ip_addresses(list(hosts.keys()))

    for host, count in hosts.items():
        print(f"{names[host]} {count:,}")


def main():
    parser = argparse.ArgumentParser(description="Parse AWS log data.")
    parser.add_argument(
        "url",
        help="Url to the file to parse",
    )
    parser.add_argument(
        "--count-hosts",
        help="Count the number of hosts",
    )

    args = parser.parse_args()

    parsed = urlparse(args.url)

    if parsed.scheme == "file":
        entries = parse_file(parsed.path)
        count_hosts(entries)
