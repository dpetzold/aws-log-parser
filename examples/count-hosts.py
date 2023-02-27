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
    python examples/count-hosts.py \
        --log-type CloudFront \
        s3://aws-logs-test-data/cloudfront-multiple.log
    """

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

    args = parser.parse_args()

    ip_attr = "client_ip" if args.log_type == LogType.CloudFront else "client.ip"

    entries = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
    ).read_url(args.url)

    count_ips(entries, ip_attr)


main()
