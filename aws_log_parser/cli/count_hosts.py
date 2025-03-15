from collections import Counter

from rich.console import Console
from rich.table import Table

console = Console()


def count_hosts(entries):
    counter = Counter([entry.client_ip for entry in entries])

    table = Table(show_header=True)
    table.add_column("", justify="left")
    table.add_column("ClientIP", justify="left")
    table.add_column("Requests", justify="right")
    table.add_column("%", justify="right")

    total = counter.total()
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
