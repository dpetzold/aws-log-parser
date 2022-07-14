#!/bin/env python

import argparse

from collections import Counter
from operator import attrgetter

from aws_log_parser import AwsLogParser, LogType


def count_ips(entries, ip_attr):

    counter = Counter(attrgetter(ip_attr)(entry) for entry in entries)

    for ip, count in sorted(counter.items()):
        print(f"{ip}: {count}")


def main():
    """
    python examples/count-hosts-gzip-alb.py \
        s3://aws-logs-test-data/test-alb/AWSLogs/111111111111/elasticloadbalancing/us-east-1/2022/01/01
    """

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

    args = parser.parse_args()

    entries = AwsLogParser(
        log_type=LogType.LoadBalancer,
        profile=args.profile,
        region=args.region,
        file_suffix=".gz"
    ).read_url(args.url)

    count_ips(entries, "client.ip")


main()
