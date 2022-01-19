import argparse
import logging
import pandas

from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from ..interface import AwsLogParser
from ..models import LogType

console = Console()
logger = logging.getLogger(__name__)


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
    for i, pair in enumerate(sorted(counter.items(), key=lambda t: t[1]), 1):
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


def public_info(log_entries):

    # print(f"public_info: {len(list(log_entries))}")

    df = pandas.DataFrame(
        [
            {
                "client_ip": log_entry.client_ip,
                # "hostname": log_entry.hostname,
                # "network": log_entry.network,
                "browser_family": log_entry.user_agent_obj.browser.family,
            }
            for log_entry in log_entries
        ]
    )

    if False:
        from pprint import pprint

        pprint(next(log_entries))

        df = pandas.DataFrame(log_entries)

    pandas.set_option("display.max_columns", None)

    grouped = (
        df.groupby(
            [
                "client_ip",
                # "network",
                # "hostname",
                "browser_family",
            ],
            as_index=False,
        )
        .size()
        .sort_values("size", ascending=False)
    ).rename(
        columns={
            "size": "Requests",
            "client_ip": "ClientIp",
            # "network": "Network",
            # "hostname": "Hostname",
        }
    )

    print(grouped[:5])


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

    logging.basicConfig(
        level="DEBUG" if args.verbose else "INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    log_entries = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
        verbose=args.verbose,
        plugin_paths=[
            Path(__file__).parents[2] / "plugins",
        ],
        plugins=[
            # "instance_id:AwsPluginInstanceId",
            # "instance_name:AwsPluginInstanceName",
            # "dns_resolver:IpResolverPlugin",
            # "radb:RadbPlugin",
            "user_agent:UserAgentPlugin",
        ],
    ).read_url(args.url)

    # count_hosts(log_entries)
    public_info(log_entries)
