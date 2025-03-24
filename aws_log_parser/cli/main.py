import asyncio
import argparse
import logging
import sys

from importlib import import_module
from pathlib import Path

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
        "--run-async",
        action="store_true",
        default=False,
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
        "--file-suffix",
        default=".gz",
        help="The file suffix to filter on.",
    )

    parser.add_argument(
        "--regex-filter",
        help="The regex filter.",
    )

    parser.add_argument(
        "--sort-key",
        help="The sort the S3 objects with this key.",
    )

    parser.add_argument(
        "--concurrency",
        help="Number of concurrent downloads.",
        default=3,
        type=int,
    )

    args = parser.parse_args()

    if args.run_async:
        asyncio.run(load_module(args.function)(args))
    else:
        load_module(args.function)(args)
