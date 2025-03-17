from collections import Counter
from io import BytesIO
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import progress as rich_progress

from ..io import FileIterator
from ..interface import AwsLogParser

console = Console()

counter = Counter()


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


def download_objects(aws_log_parser, progress, task_id, bucket, s3_objects):
    for i, s3_object in enumerate(s3_objects, 1):
        key = s3_object["Key"]

        progress.update(
            task_id,
            filename=Path(s3_object["Key"]).name,
            total=s3_object["Size"],
        )

        progress.console.log(f"Downloading {s3_object['Key']}")
        progress.start_task(task_id)

        contents = BytesIO()

        aws_log_parser.s3_client.client.download_fileobj(
            bucket,
            key,
            contents,
            Callback=lambda x: progress.update(task_id, advance=x),
        )

        entries = []
        for entry in aws_log_parser.parse(
            FileIterator(
                fileobj=contents,
                gzipped=key.endswith(".gz"),
            )
        ):
            entries.append(entry)
            progress.update(task_id, advance=1)

        if i == 3:
            break


def count_hosts(args):
    aws_log_parser = AwsLogParser(
        log_type=args.log_type,
        profile=args.profile,
        region=args.region,
        verbose=args.verbose,
    )

    # with console.status("[bold green]Listing objects..."):
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

    with rich_progress.Progress(
        rich_progress.TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        rich_progress.BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        rich_progress.DownloadColumn(),
        "•",
        rich_progress.TransferSpeedColumn(),
        "•",
        rich_progress.TimeRemainingColumn(),
    ) as progress:

        task_id = progress.add_task("download", filename="notset", start=False)

        download_objects(aws_log_parser, progress, task_id, bucket, s3_objects)
