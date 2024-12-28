#!/bin/env python

import argparse
import textwrap

from collections import Counter
from operator import attrgetter

from aws_log_parser import AwsLogParser, LogType


def count_ips(entries, ip_attr):
    counter = Counter(attrgetter(ip_attr)(entry) for entry in entries)

    for ip, count in sorted(counter.items()):
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

    # LoadBalancer all with the prefix on S3.

    python examples/count-hosts.py \\
        --log-type LoadBalancer \\
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
