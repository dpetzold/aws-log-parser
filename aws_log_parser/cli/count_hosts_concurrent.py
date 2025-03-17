import asyncio
import time
from collections import Counter

from rich.console import Console
from rich.table import Table
from rich import progress as rich_progress

from ..interface import AwsLogParser

console = Console()

counter = Counter()

counter_lock = asyncio.Lock()


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


async def download_worker(
    aws_log_parser,
    bucket,
    progress,
    task_progress,
    queue,
):
    while True:
        s3_object = await queue.get()

        progress.update(
            task_progress,
            filename=s3_object["Key"],
            total=s3_object["Size"],
        )

        progress.console.log(f"Downloading {s3_object['Key']}")

        entries = []
        for entry in aws_log_parser.parse(
            aws_log_parser.s3_client.read_key(bucket, s3_object["Key"])
        ):
            entries.append(entry)
            progress.update(task_progress, advance=1)

        async with counter_lock:
            counter.update([entry.client_ip for entry in entries])

        queue.task_done()


async def download_objects(aws_log_parser, bucket, s3_objects):
    queue = asyncio.Queue()

    for s3_object in s3_objects:
        queue.put_nowait(s3_object)

    progress = rich_progress.Progress(
        rich_progress.TextColumn(
            "[bold blue]{taws_log_parser.parseask.fields[filename]}", justify="right"
        ),
        rich_progress.BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        rich_progress.DownloadColumn(),
        "•",
        rich_progress.TransferSpeedColumn(),
        "•",
        rich_progress.TimeRemainingColumn(),
    )

    tasks = []
    for i in range(3):
        progress_task = progress.add_task(f"download-{i}", start=False)

        task = asyncio.create_task(
            download_worker(aws_log_parser, bucket, progress, progress_task, queue)
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

    await download_objects(aws_log_parser, bucket, s3_objects)
