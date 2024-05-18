#!/bin/env python

import argparse
from rich.console import Console
from rich.table import Table

from collections import Counter
from operator import attrgetter

from aws_log_parser import AwsLogParser, LogType

console = Console()


def count_ips(entries, attr_name, num_results):
    table = Table()

    counter = Counter(attrgetter(attr_name)(entry) for entry in entries)

    table.add_column(attr_name)
    table.add_column("count")

    for attr, count in sorted(counter.most_common(num_results)):
        table.add_row(attr, str(count))

    console.print(table)


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
        "--count",
        default=20,
        type=int,
        help="Show this number of results.",
    )
    parser.add_argument(
        "--filter",
        help="Filter filenames that match this string.",
    )
    parser.add_argument(
        "--suffix",
        help="Filter filenames the specified suffix.",
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
        "--attr",
        help="The attribute to count.",
    )

    args = parser.parse_args()

    count_attr = (
        args.attr
        if args.attr
        else "client_ip"
        if args.log_type == LogType.CloudFront
        else "client.ip"
    )

    entries = AwsLogParser(
        log_type=args.log_type,
        file_suffix=args.suffix,
        profile=args.profile,
        region=args.region,
    ).read_url(args.url, filter=args.filter)

    count_ips(entries, count_attr, args.count)


main()
