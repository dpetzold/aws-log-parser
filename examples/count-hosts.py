#!/bin/env python

import argparse

from collections import Counter

from aws_log_parser import AwsLogParser, LogType


def count_ips(parser, url):

    entries = parser.read_url(url)

    counter = Counter()

    for entry in entries:
        counter[entry.client_ip] += 1

    for ip, count in counter.items():
        print(f"{ip}: {count}")


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

    args = parser.parse_args()

    parser = AwsLogParser(
        log_type=LogType.CloudFront,
        profile=args.profile,
        region=args.region,
    )

    count_ips(parser, args.url)


main()
