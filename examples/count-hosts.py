#!/bin/env python

import argparse
import json
import dataclasses
import textwrap

from collections import Counter
from operator import attrgetter

from aws_log_parser import AwsLogParser, LogType


def _count_ips(entries, ip_attr):
    for entry in entries:
        print(json.dumps(dataclasses.asdict(entry), indent=4, default=str))
        break


def count_ips(entries, ip_attr):
    ips = [
        "18.155.202.126",
        "18.155.202.72",
        "18.155.202.113",
        "18.155.202.101",
    ]

    filtered = [entry for entry in entries if entry.dstaddr in ips]

    for entry in filtered:
        print(json.dumps(dataclasses.asdict(entry), indent=4, default=str))
        break


def _count_ips(entries, ip_attr):
    """
    184.72.225.4: 350160
    34.231.137.156: 305434
    184.72.231.0: 4823
    184.72.224.249: 3074
    184.72.227.124: 2452
    71.247.202.102: 1
    """

    counter = Counter(entry.client_ip for entry in entries if entry.http_method == "POST")

    for ip, count in counter.most_common():
        print(f"{ip}: {count}")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Parse AWS log data.",
        epilog=textwrap.dedent(
            """
Examples:

    # All local files in the given path.

    python examples/count-hosts.py \\
        --log-type CloudFront \\
        file://$(pwd)/logfiles/

    # CloudFront single file on S3.

    python examples/count-hosts.py \\
        --log-type CloudFront \\
        s3://aws-logs-test-data/cloudfront-multiple.log

    # LoadBalancer all with the regex search match on S3.

    python examples/count-hosts.py \\
        --log-type LoadBalancer \\
        --regex-filter='E110AAAAAAAAAA\\.2024\\-05\\-13\\-13' \\
        --file-suffix='.gz' \\
        s3://aws-logs-test-data/test-alb/AWSLogs/111111111111/elasticloadbalancing/us-east-1/2022/
"""
        ),
    )

    parser.add_argument(
        "url",
        help="Url to the file to parse",
    )
    parser.add_argument(
        "--log-type",
        type=lambda x: getattr(LogType, x),
        default="CloudFront",
        help="The the log type.",
    )

    parser.add_argument(
        "--file-suffix",
        default=".log",
        help="The file suffix to filter on.",
    )

    parser.add_argument(
        "--regex-filter",
        help="The regex filter.",
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
        "--verbose",
        action="store_true",
        help="Enable verbose mode.",
    )

    args = parser.parse_args()

    ip_attr = "client_ip" if args.log_type == LogType.CloudFront else "client.ip"

    entries = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
        verbose=args.verbose,
        file_suffix=args.file_suffix,
        regex_filter=args.regex_filter,
    ).read_url(args.url)

    count_ips(entries, ip_attr)


main()
