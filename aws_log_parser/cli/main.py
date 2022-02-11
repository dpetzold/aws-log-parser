import argparse
import logging
import pandas
import operator

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

    print(df[:limit])


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
        "--suffix",
        default=".log",
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

    plugins = []

    display_attrs = {
        "client_ip": "client_ip",
    }

    if args.profile == "aws":
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
    elif args.profile == "public":
        plugins.extend(
            [
                "dns_resolver:IpResolverPlugin",
                "radb:RadbPlugin",
                "user_agent:UserAgentPlugin",
            ]
        )
        display_attrs.update(
            {
                "hostname": "hostname",
                "network": "network",
                "os_family": "user_agent_obj.os.family",
                "browser_family": "user_agent_obj.browser.family",
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
    ).read_url(args.url)

    display_entries(log_entries, display_attrs)
