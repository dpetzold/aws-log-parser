from collections import Counter

from rich.console import Console
from rich.table import Table

console = Console()


def count_hosts(entries):
    counter = Counter()
    for entry in entries:
        counter[
            (
                entry.instance_name
                if hasattr(entry, "instance_name") and entry.instance_name
                else (entry.instance_id if entry.instance_id else entry.client_ip)
            )
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
            f"({(count / total) * 100:.2f}%)",
            end_section=i == len(counter),
        )

    table.add_row("", "Total", f"{total:,}", "")

    console.print(table)
