"""CLI for listing top-level windows without using the mouse."""

from __future__ import annotations

from dataclasses import asdict

from rich.console import Console
from rich.table import Table
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from automation.window_finder import WindowFinder, WindowInfo
from inspector.formatters import error_panel
from utils.logging import configure_logging

app = typer.Typer(help="List top-level windows discovered from the desktop root.")


@app.command()
def main(
    title: str | None = typer.Option(None, "--title", "-t", help="Filter by title substring."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Print Title, ClassName, PID, Handle, and BoundingRectangle for top-level windows."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        finder = WindowFinder(UIAutomationClient())
        rows = [info for _, info in finder.list_windows(title=title)]
        _print_windows(rows, console)
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


def _print_windows(windows: list[WindowInfo], console: Console) -> None:
    table = Table(title=f"Top-level Windows ({len(windows)})", show_header=True)
    for column in ("Title", "ClassName", "PID", "Handle", "BoundingRectangle"):
        table.add_column(column)
    for window in windows:
        table.add_row(
            window.title,
            window.class_name,
            "" if window.pid is None else str(window.pid),
            "" if window.handle is None else str(window.handle),
            str(asdict(window.bounding_rectangle)),
        )
    console.print(table)


if __name__ == "__main__":
    app()
