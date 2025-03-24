import asyncio
import logging
import time
from collections import Counter
from io import BytesIO
from pathlib import Path

import aioboto3

from rich.console import Console
from rich.table import Table
from rich import progress as rich_progress

from ..interface import AwsLogParser
from ..io import FileIterator

console = Console()

counter = Counter()

counter_lock = asyncio.Lock()

logger = logging.getLogger(__name__)


def print_results(counter):
    table = Table(show_header=True)
    table.add_column("", justify="left")
    table.add_column("ClientIP", justify="left")
    table.add_column("Requests", justify="right")
    table.add_column("%", justify="right")

    total = counter.total()  # type: ignore
    for i, pair in enumerate(sorted(counter.items(), key=lambda t: t[1]), 1):
        client_ip, count = pair
        table.add_row(
            str(i),
            client_ip,
            f"{count:,}",
            f"({(count / total) * 100:.2f}%)",
            end_section=i == len(counter),
        )

    table.add_row("", "Total", f"{total:,}", "")

    console.print(table)


def key_display(key):
    path = Path(key)
    split = path.name.split(".")
    split.pop(0)
    return ".".join(split)


async def download_worker(
    name,
    session,
    aws_log_parser,
    bucket,
    progress,
    progress_task,
    total_progress_task,
    queue,
):
    def update_progress(size):
        progress.update(progress_task, advance=size)
        progress.update(total_progress_task, advance=size)

    progress.console.log(f"Started {name}")

    while True:
        s3_object = await queue.get()

        key = s3_object["Key"]

        progress.update(
            progress_task,
            total=s3_object["Size"],
            filename=f"Downloading {key_display(key)}",
        )

        progress.console.log(f"Downloading {key_display(key)} {s3_object['Size']}")

        contents = BytesIO()

        async with session.client("s3") as s3_client:
            await s3_client.download_fileobj(
                bucket,
                key,
                contents,
                Callback=update_progress,
            )

        contents.seek(0)

        lines = list(
            line
            for line in FileIterator(
                fileobj=contents,
                gzipped=key.endswith(".gz"),
            )
        )

        progress.reset(
            progress_task,
            filename=f"Parsing {key_display(key)}",
            completed=s3_object["Size"],
            total=len(lines),
            refresh=True,
        )

        progress.console.log(f"Parsing {key_display(key)} {len(lines)}")

        entries = []
        for entry in aws_log_parser.parse(lines):
            entries.append(entry)
            # progress.update(progress_task, advance=1)

        async with counter_lock:
            counter.update([entry.client_ip for entry in entries])

        # progress.reset(
        #     progress_task,
        #    filename=f"Parsing {key_display(key)}",
        #    refresh=True,
        # )

        queue.task_done()


async def download_objects(aws_log_parser, bucket, s3_objects, num_workers):
    queue = asyncio.Queue()

    session = aioboto3.Session()

    progress = rich_progress.Progress(
        rich_progress.TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        rich_progress.BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        rich_progress.DownloadColumn(),
        "•",
        rich_progress.TransferSpeedColumn(),
        "•",
        rich_progress.TimeRemainingColumn(),
        auto_refresh=False,
    )

    progress.start()

    total_size = 0
    for s3_object in s3_objects:
        queue.put_nowait(s3_object)
        total_size += s3_object["Size"]

    total_progress_task_id = progress.add_task(
        "Total Progress",
        filename="Total Progress",
        total=total_size,
    )

    tasks = []
    for i in range(num_workers):
        progress_task_id = progress.add_task(
            f"downloader-{i}",
            filename=f"downloader-{i}",
            start=False,
        )

        task = asyncio.create_task(
            download_worker(
                f"downloader-{i}",
                session,
                aws_log_parser,
                bucket,
                progress,
                progress_task_id,
                total_progress_task_id,
                queue,
            )
        )

        tasks.append(task)

    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    console.log("====")
    console.log(f"3 workers worked in parallel for {total_slept_for:.2f} seconds")

    print_results(counter)


async def count_hosts(args):
    aws_log_parser = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
        verbose=args.verbose,
    )

    with console.status("[bold green]Listing objects..."):
        bucket, prefix = aws_log_parser.s3_client.parse_url(args.url)

        s3_objects = list(
            aws_log_parser.s3_client.filter_objects(
                bucket,
                prefix,
                endswith=args.file_suffix,
                regex_filter=args.regex_filter,
                sort_key=args.sort_key,
            )
        )

        console.log(f"Found {len(s3_objects)} S3 objects")

    await download_objects(aws_log_parser, bucket, s3_objects, args.concurrency)
