import argparse
import logging
import pandas
import operator
import sqlite3

from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from ..interface import AwsLogParser
from ..models import LogType

console = Console()
logger = logging.getLogger(__name__)


for name in ["boto", "urllib3", "s3transfer", "boto3", "botocore", "nose"]:
    logging.getLogger(name).setLevel(logging.CRITICAL)


def display_entries(log_entries, attrs, limit=10):

    pandas.set_option("max_columns", None)  # show all cols
    pandas.set_option("max_colwidth", None)
    pandas.set_option("display.max_columns", None)

    df = (
        pandas.DataFrame(
            [
                {
                    attr_name: operator.attrgetter(attr_key)(log_entry)
                    for attr_name, attr_key in attrs.items()
                }
                for log_entry in log_entries
            ]
        )
        .groupby(
            list(attrs.keys()),
            as_index=False,
        )
        .size()
        .sort_values("size", ascending=False)
        .rename(
            columns={
                "size": "Requests",
            }
        )
    )

    for _, row in df[:limit].iterrows():
        print(row)

    sum_requests = sum(row["Requests"] for _, row in df.iterrows())
    print(f"Total Requests: {sum_requests:,}")


def local_table(table_name, batched):

    con = sqlite3.connect(f"{table_name}.db")
    cur = con.cursor()
    cur.execute(f"create table {table_name} (client_ip, instance_id, instance_name)")

    for batch in batched:
        tuples = [
            (log_entry.client_ip, log_entry.instance_id, log_entry.instance_name)
            for log_entry in batch
        ]

        print(len(tuples))

        cur.executemany(f"insert into {table_name} values (?, ?, ?)", tuples)

    con.commit()
    con.close()


def read_table(table_name):

    con = sqlite3.connect(table_name)
    cur = con.cursor()

    cur.execute(
        f"""
SELECT
    COUNT(*) as count,
    client_ip,
    instance_id,
    instance_name
FROM
    {table_name}
GROUP BY
    client_ip,
    instance_id,
    instance_name
ORDER BY
    count desc
"""
    )

    for row in cur.fetchall():
        print(row)


def main():

    parser = argparse.ArgumentParser(description="Parse AWS log data.")
    parser.add_argument(
        "url",
        nargs="+",
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
        "--suffix",
        default=".log",
    )

    parser.add_argument("--table-name")

    parser.add_argument("--read-table")

    parser.add_argument("--traffic-profile", choices=["public", "aws"], default=None)

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    if args.read_table:
        return read_table(args.read_table)

    plugins = []

    display_attrs = {
        "client_ip": "client_ip",
    }

    if args.traffic_profile == "aws":
        plugins.extend(
            [
                "instance_id:AwsPluginInstanceId",
                "instance_name:AwsPluginInstanceName",
            ]
        )
        display_attrs.update(
            {
                "instance_id": "instance_id",
                "instance_name": "instance_name",
            }
        )
    elif args.traffic_profile == "public":
        plugins.extend(
            [
                "dns_resolver:IpResolverPlugin",
                "radb:RadbPlugin",
                "user_agent:UserAgentPlugin",
            ]
        )
        display_attrs.update(
            {
                "user_agent": "user_agent",
                "os_family": "user_agent_obj.os.family",
                "browser_family": "user_agent_obj.browser.family",
                "elb_status_code": "elb_status_code",
                "target_status_code": "target_status_code",
            }
        )

    log_entries = AwsLogParser(
        log_type=args.log_type,
        aws_profile=args.aws_profile,
        aws_region=args.aws_region,
        verbose=args.verbose,
        file_suffix=args.suffix,
        plugin_paths=[
            Path(__file__).parents[2] / "plugins",
        ],
        plugins=plugins,
    ).read_urls(args.url)

    if args.table_name:
        local_table(args.table_name, log_entries)
    else:
        display_entries(log_entries, display_attrs)
