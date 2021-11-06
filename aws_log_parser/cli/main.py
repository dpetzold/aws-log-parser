import argparse

import logging

from collections import Counter
from urllib.parse import urlparse

from ..parser import AwsLogParser
from ..models import LogType

logger = logging.getLogger(__name__)


def read_file(path):
    with open(path) as log_data:
        yield from AwsLogParser(
            log_type=LogType.ClassicLoadBalancer,
        ).parse(log_data.readlines())


def read_files(paths):
    for path in paths:
        yield from read_file(path)


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
        entries = read_file(parsed.path)

    elif parsed.scheme == "s3":
        entries = read_s3(parsed.netloc, parsed.path.lstrip("/"), endswith=".log")

    else:
        raise ValueError(f"Unknown scheme {parsed.scheme}")

    count_hosts(entries)
