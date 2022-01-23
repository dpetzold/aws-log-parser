import argparse
import logging
import pandas

from collections import Counter
from pathlib import Path
from pprint import pprint

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from ..interface import AwsLogParser
from ..models import LogType

console = Console()
logger = logging.getLogger(__name__)


for name in ["boto", "urllib3", "s3transfer", "boto3", "botocore", "nose"]:
    logging.getLogger(name).setLevel(logging.CRITICAL)


def aws_info(entries):
    counter = Counter()

    for entry in entries:
        counter[
            entry.instance_name
            if hasattr(entry, "instance_name") and entry.instance_name
            else (entry.instance_id if entry.instance_id else entry.client_ip)
        ] += 1

    table = Table(show_header=True)
    table.add_column("", justify="left")
    table.add_column("Instance Name", justify="left")
    table.add_column("Requests", justify="right")
    table.add_column("%", justify="right")

    total = counter.total()
    for i, pair in enumerate(
        sorted(counter.items(), key=lambda t: t[1], reverse=True), 1
    ):
        instance_name, count = pair
        table.add_row(
            str(i),
            instance_name,
            f"{count:,}",
            f"({(count/total) * 100:.2f}%)",
            end_section=i == len(counter),
        )

    table.add_row("", "Total", f"{total:,}", "")

    console.print(table)


def public_info(log_entries, limit=10):

    df = pandas.DataFrame(
        [
            {
                "client_ip": log_entry.client_ip,
                "hostname": log_entry.hostname,
                "network": log_entry.network,
                "os_family": log_entry.user_agent_obj.os.family,
                "browser_family": log_entry.user_agent_obj.browser.family,
            }
            for log_entry in log_entries
        ]
    )

    pandas.set_option("display.max_columns", None)

    grouped = (
        df.groupby(
            [
                "client_ip",
                "network",
                "hostname",
                "browser_family",
                "os_family",
            ],
            as_index=False,
        )
        .size()
        .sort_values("size", ascending=False)
        .rename(
            columns={
                "size": "Requests",
                "client_ip": "ClientIp",
                "network": "Network",
                "hostname": "Hostname",
            }
        )
    )

    print(grouped[:limit])


def _():
    table = Table(show_header=True)
    table.add_column("", justify="left")
    table.add_column("ClientIp", justify="left")
    table.add_column("Requests", justify="right")
    table.add_column("Network", justify="right")
    table.add_column("Hostname", justify="right")
    # table.add_column("UserAgent", justify="right")
    table.add_column("%", justify="right")

    """
    for
        table.add_row(
            str(i),
            instance_name,
            f"{count:,}",
            f"({(count/total) * 100:.2f}%)",
            end_section=i == len(client_ips),
        )

    table.add_row("", "Total", f"{total:,}", "")

    console.print(table)
    """


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
        "--log-level",
        choices=[
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
        ],
        default="INFO",
        help="The the logging level.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--aws-profile",
        help="The aws profile to use.",
    )

    parser.add_argument(
        "--aws-region",
        help="The aws region to use.",
    )

    parser.add_argument(
        "--count-hosts",
        help="Count the number of hosts",
    )

    parser.add_argument(
        "--instance-id",
    )

    parser.add_argument("--profile", choices=["public", "aws"], default=None)

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    if args.profile == "aws":
        plugins = [
            "instance_id:AwsPluginInstanceId",
            "instance_name:AwsPluginInstanceName",
        ]
        display_func = aws_info
    elif args.profile == "public":
        plugins = [
            "dns_resolver:IpResolverPlugin",
            "radb:RadbPlugin",
            "user_agent:UserAgentPlugin",
        ]
        display_func = public_info
    else:
        plugins = []
        display_func = pprint

    log_entries = AwsLogParser(
        log_type=args.log_type,
        aws_profile=args.aws_profile,
        aws_region=args.aws_region,
        verbose=args.verbose,
        plugin_paths=[
            Path(__file__).parents[2] / "plugins",
        ],
        plugins=plugins,
    ).read_url(args.url)

    display_func(log_entries)
