import argparse
import logging

from collections import Counter

from ..interface import AwsLogParser
from ..models import LogType

logger = logging.getLogger(__name__)


def count_hosts(entries):
    hosts = Counter()
    for entry in entries:
        hosts[
            entry.instance_name
            if entry.instance_name
            else (entry.instance_id if entry.instance_id else entry.client_ip)
        ] += 1

    for instance_name, count in sorted(hosts.items(), key=lambda t: t[1]):
        print(f"{instance_name}: {count:,}")


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
        "--verbose",
        action="store_true",
        default=False,
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

    parser.add_argument(
        "--instance-id",
    )

    args = parser.parse_args()

    log_entries = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
        verbose=args.verbose,
        plugin_paths=[
            "/home/derrick/src/aws-log-parser/plugins",
        ],
        plugins=[
            "instance_id:AwsLogParserPluginInstanceId",
            "instance_name:AwsLogParserPluginInstanceName",
        ],
    ).read_url(args.url)

    count_hosts(log_entries)
