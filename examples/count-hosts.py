#!/bin/env python

from collections import Counter

from aws_log_parser import AwsLogParser, LogType


def count_ips():

    parser = AwsLogParser(log_type=LogType.CloudFront, profile="personal")
    entries = parser.read_url("s3://aws-logs-test-data/cloudfront-multiple.log")

    counter = Counter()

    for entry in entries:
        counter[entry.client_ip] += 1

    for ip, count in counter.items():
        print(f"{ip}: {count}")


count_ips()
