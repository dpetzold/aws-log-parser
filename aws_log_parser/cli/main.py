import argparse
import logging
import sys

from importlib import import_module
from pathlib import Path

from ..interface import AwsLogParser
from ..models import LogType

logger = logging.getLogger(__name__)


def load_module(path: str):
    module_name, func_name = path.split(":", 1)

    module_path = Path(module_name).resolve()
    sys.path.insert(0, str(module_path.parent))

    if module_path.is_file():
        import_name = module_path.with_suffix("").name
    else:
        import_name = module_path.name

    try:
        module = import_module(import_name)
    except ModuleNotFoundError as error:
        if error.name == import_name:
            raise ValueError(f"Cannot load application from '{path}', module not found.")
        else:
            raise

    try:
        return eval(func_name, vars(module))
    except NameError:
        raise ValueError(f"Cannot load application from '{path}', application not found.")


def main():
    parser = argparse.ArgumentParser(description="Parse AWS log data.")

    parser.add_argument(
        "function",
        help="Function to read the parsed data",
    )

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
        # plugin_paths=[
        #     Path(__file__).parents[2] / "plugins",
        # ],
        # plugins=[
        #     "instance_id:AwsPluginInstanceId",
        #     "instance_name:AwsPluginInstanceName",
        # ],
    ).read_url(args.url)

    func = load_module(args.function)
    func(log_entries)
